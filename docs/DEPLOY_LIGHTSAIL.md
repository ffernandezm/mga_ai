# Despliegue controlado en AWS Lightsail

Esta guia usa Ubuntu 24.04, 2 vCPU, 4 GB RAM, 80 GB SSD, Docker Compose y Nginx
del host. Sustituya `mga.example.com` por el dominio real en todos los comandos.

## 1. Instancia y red

1. Cree la instancia Lightsail y asigne una IP estatica.
2. En el firewall abra TCP 22 solo desde IPs administrativas y TCP 80/443 desde Internet.
3. No abra 5432, 8000 ni 8080.
4. Cree un registro DNS `A` hacia la IP estatica y espere su propagacion.

## 2. Docker y Nginx

Instale Docker Engine y el plugin Compose desde el repositorio oficial de Docker
para Ubuntu. Instale el proxy, Certbot y la utilidad de autenticacion:

```bash
sudo apt update
sudo apt install -y nginx apache2-utils certbot python3-certbot-nginx
docker --version
docker compose version
sudo systemctl enable --now nginx
```

Agregue el usuario operativo al grupo `docker`, cierre la sesion y vuelva a entrar.

## 3. Aplicacion y entorno

```bash
git clone URL_DEL_REPOSITORIO.git mga_ai
cd mga_ai
cp production.env.example .env.production
chmod 600 .env.production
```

Cambie todos los `CHANGE_ME`, configure el dominio HTTPS final en `PUBLIC_URL` y
solo la clave del proveedor elegido. La contrasena PostgreSQL puede contener
caracteres especiales: se pasa como campo separado y el backend codifica la URL.
En `.env.production`, escriba el valor entre comillas simples para que Compose
preserve literalmente caracteres como `$`, por ejemplo `POSTGRES_PASSWORD='...'`.

Con OpenAI, `OPENAI_MODEL` debe ser un ID real habilitado en la cuenta. El
repositorio no define aliases. Nunca versione `.env.production`.

```bash
docker compose --env-file .env.production config --quiet
docker compose --env-file .env.production build --pull
docker compose --env-file .env.production up -d
docker compose --env-file .env.production ps
docker compose --env-file .env.production logs --tail=200 backend
```

Con `RAG_WARMUP_ON_START=true`, el primer arranque construye el indice 2023 antes
de habilitar frontend. Reserve hasta 5 minutos. Los reinicios normales reutilizan
el volumen y son mucho mas rapidos.

## 4. Basic Authentication y proxy

Cree usuarios fuera del repositorio. Los comandos solicitan la contrasena:

```bash
sudo htpasswd -c /etc/nginx/.htpasswd_mga evaluador1
sudo htpasswd /etc/nginx/.htpasswd_mga evaluador2
sudo chown root:www-data /etc/nginx/.htpasswd_mga
sudo chmod 640 /etc/nginx/.htpasswd_mga
```

Cree `/etc/nginx/sites-available/mga`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name mga.example.com;

    auth_basic "Evaluacion MGA";
    auth_basic_user_file /etc/nginx/.htpasswd_mga;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

La autenticacion en `server` protege React, `/api`, health y readiness. El host
sobrescribe las cabeceras para no aceptar valores falsificados desde Internet.

```bash
sudo ln -s /etc/nginx/sites-available/mga /etc/nginx/sites-enabled/mga
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
curl -I http://mga.example.com
```

La ultima solicitud debe responder `401` sin credenciales.

## 5. TLS con Let's Encrypt

```bash
sudo certbot --nginx -d mga.example.com
sudo nginx -t
sudo systemctl reload nginx
sudo certbot renew --dry-run
curl -u evaluador1 https://mga.example.com/api/ready
```

Escriba la contrasena cuando `curl` la solicite; no la incluya en scripts.

## 6. Validacion operativa

```bash
docker compose --env-file .env.production ps
docker compose --env-file .env.production exec backend curl --fail http://localhost:8000/health
docker compose --env-file .env.production exec backend curl --fail http://localhost:8000/ready
docker compose --env-file .env.production exec backend ls -lh /data/rag-index
docker compose --env-file .env.production exec backend cat /data/rag-index/index_metadata.json
sudo ss -lntp | grep -E ':(80|443|8080|8000|5432)\b'
docker stats --no-stream
docker system df
```

El host debe escuchar 80/443 y `127.0.0.1:8080`; no 8000 ni 5432. La metadata
RAG debe indicar `Documento_conceptual_2023.pdf`.

## 7. Actualizacion

```bash
cd mga_ai
git pull --ff-only
docker compose --env-file .env.production config --quiet
docker compose --env-file .env.production build
docker compose --env-file .env.production up -d
docker compose --env-file .env.production ps
curl -u evaluador1 https://mga.example.com/api/ready
docker image prune -f
```

No use `docker compose down -v`: elimina PostgreSQL y el indice RAG.

## 8. Backup y restauracion

```bash
mkdir -p backups
docker compose --env-file .env.production exec -T db \
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom' \
  > "backups/mga-$(date +%F-%H%M).dump"
```

Copie los respaldos fuera de Lightsail. Para restaurar en una base vacia durante
una ventana de mantenimiento:

```bash
docker compose --env-file .env.production stop backend frontend
cat backups/ARCHIVO.dump | docker compose --env-file .env.production exec -T db \
  sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists'
docker compose --env-file .env.production up -d
```

Pruebe periodicamente la restauracion en una instancia o base separada.

## 9. Logs y diagnostico

Compose rota cada log a 10 MB y conserva cinco archivos por servicio:

```bash
docker compose --env-file .env.production logs --tail=200 backend
docker compose --env-file .env.production logs --since=10m frontend
journalctl -u nginx --since "10 minutes ago"
sudo tail -n 200 /var/log/nginx/error.log
```

- `401`: Basic Authentication esta activa.
- `502`: backend no esta ready; revise migraciones, DB, proveedor e indice RAG.
- `503` en `/ready`: PostgreSQL o RAG no estan preparados.
- Rebuild RAG inesperado: compare PDF, hash y parametros con la metadata.
