allow_k8s_contexts('minikube')

yaml = helm(
    './chart',
    name='url-shortener',
    namespace='default',
    set=['namespace.create=false'],
)
k8s_yaml(yaml)

docker_build(
    'url-shortener-api-dev',
    './api',
    dockerfile='./api/Dockerfile.dev',
    live_update=[
        sync('api/main.py', '/app/main.py'),
        sync('api/app', '/app/app'),
    ],
)

docker_build(
    'url-shortener-client-dev',
    './client',
    dockerfile='./client/Dockerfile.dev',
    live_update=[
        sync('client/src', '/app/src'),
        sync('client/index.html', '/app/index.html'),
        sync('client/vite.config.ts', '/app/vite.config.ts'),
        sync('client/package.json', '/app/package.json'),
    ],
)

k8s_resource('api', port_forwards=['8000:8000'])
k8s_resource('client', port_forwards=['8080:8080'])
