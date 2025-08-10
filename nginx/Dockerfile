FROM nginx:1.25.5-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY docs/ /usr/share/nginx/html/api/docs/
RUN mkdir -p /usr/share/nginx/html/ /user/share/nginx/html/media
