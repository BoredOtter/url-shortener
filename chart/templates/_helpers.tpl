{{- define "url-shortener.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "url-shortener.labels" -}}
app.kubernetes.io/name: {{ include "url-shortener.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
