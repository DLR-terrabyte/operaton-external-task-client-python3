FROM operaton/operaton:2.1.0
USER root
COPY --chown=operaton:operaton ./engine-rest/web.xml /operaton/webapps/engine-rest/WEB-INF/web.xml
