# ⚙️ Configuration

## 🌎 Environment Variables

[**`.env.example`**](https://github.com/{{cookiecutter.repo_owner}}/{{cookiecutter.repo_name}}/blob/main/.env.example):

```sh
## --- Environment variable --- ##
ENV=LOCAL
DEBUG=false
# TZ=Asia/Seoul


## --- DB configs --- ##
{{cookiecutter.env_prefix}}DB_HOST=localhost
{{cookiecutter.env_prefix}}DB_PORT=5432
{{cookiecutter.env_prefix}}DB_USERNAME={{cookiecutter.project_abbr}}_admin
{{cookiecutter.env_prefix}}DB_PASSWORD="{{cookiecutter.env_prefix}}DB_PASSWORD123" # !!! CHANGE THIS TO RANDOM PASSWORD !!!
{{cookiecutter.env_prefix}}DB_DATABASE={{cookiecutter.project_abbr}}_db
# {{cookiecutter.env_prefix}}DB_DSN_URL="postgresql+psycopg://{{cookiecutter.project_abbr}}_admin:{{cookiecutter.env_prefix}}DB_PASSWORD123@localhost:5432/{{cookiecutter.project_abbr}}_db" # !!! CHANGE THIS TO REAL DSN URL !!!

# {{cookiecutter.env_prefix}}DB_READ_HOST=localhost
# {{cookiecutter.env_prefix}}DB_READ_PORT=5432
# {{cookiecutter.env_prefix}}DB_READ_USERNAME={{cookiecutter.project_abbr}}_admin
# {{cookiecutter.env_prefix}}DB_READ_PASSWORD="{{cookiecutter.env_prefix}}DB_PASSWORD123" # !!! CHANGE THIS TO RANDOM PASSWORD !!!
# {{cookiecutter.env_prefix}}DB_READ_DATABASE={{cookiecutter.project_abbr}}_db
# {{cookiecutter.env_prefix}}DB_READ_DSN_URL="postgresql+psycopg://{{cookiecutter.project_abbr}}_admin:{{cookiecutter.env_prefix}}DB_PASSWORD123@localhost:5432/{{cookiecutter.project_abbr}}_db" # !!! CHANGE THIS TO REAL DSN URL !!!


## -- API configs -- ##
{{cookiecutter.env_prefix}}API_PORT=8000
# {{cookiecutter.env_prefix}}API_LOGS_DIR="/var/log/{{cookiecutter.project_slug}}"
# {{cookiecutter.env_prefix}}API_DATA_DIR="/var/lib/{{cookiecutter.project_slug}}"
# {{cookiecutter.env_prefix}}API_VERSION="1"
# {{cookiecutter.env_prefix}}API_PREFIX="/api/v{api_version}"
# {{cookiecutter.env_prefix}}API_DOCS_ENABLED=true
# {{cookiecutter.env_prefix}}API_DOCS_OPENAPI_URL="{api_prefix}/openapi.json"
# {{cookiecutter.env_prefix}}API_DOCS_DOCS_URL="{api_prefix}/docs"
# {{cookiecutter.env_prefix}}API_DOCS_REDOC_URL="{api_prefix}/redoc"
```

## 🔧 Command arguments

You can customize the command arguments to debug or run the service with different commands.

[**`compose.override.yml`**](https://github.com/{{cookiecutter.repo_owner}}/{{cookiecutter.repo_name}}/blob/main/templates/compose/compose.override.dev.yml):

```yml
    command: ["/bin/bash"]
    command: ["-b", "pwd && ls -al && /bin/bash"]
    command: ["-b", "python -u -m api"]
    command: ["-b", "uvicorn main:app --host=0.0.0.0 --port={% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_PORT:-8000} --no-access-log --no-server-header --proxy-headers --forwarded-allow-ips='*'"]
```
