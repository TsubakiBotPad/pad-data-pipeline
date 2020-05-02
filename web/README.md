The *-api-cloudbuild.yaml files in the project root can be used to build the
server containers.

The containers embed the database configuration; it's imported at build time
using Secret Manager.

The admin api server also needs a pointer to the on-disk ES dir.

TODO: 
The containers are automatically redeployed from the :prod tag.
