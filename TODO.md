* Fix staticfiles
* Use https://startbootstrap.com/template/simple-sidebar
* Root view /

* I want to have two apps on Digital Ocean apps, "dev" and "prod".
"prod" is based upon "main" git branch. "dev" is based upon the
"dev" git branch. This allows me to merge PRs into "dev" and test
that they deploy, instead of maybe breaking the prod deploy.

I also need a Dockerfile that apt installs `lame libsox-fmt-all sox
ffmpeg unzip`. This is because Digital Ocean doesn't all apt on its
app platform:
https://www.digitalocean.com/community/questions/how-to-install-ffmpeg-on-app-platform
Do we need to do something as complex as this:
https://github.com/testdrivenio/django-github-digitalocean
?
Or perhaps it is this simple:
https://www.digitalocean.com/community/tutorials/how-to-build-a-django-and-gunicorn-application-with-docker#step-6-writing-the-application-dockerfile

* Create TOS and privacy policy
* Setup allauth for Google OAuth
