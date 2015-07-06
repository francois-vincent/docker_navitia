docker_navitia
=============

This project allows to create, manage and test Docker images/containers for Navitia2.
The main idea is to manage independant docker images for the different components of Navitia.
Each component's docker image being delivered synchronously with the delivery of Navitia's components.

The purppose of this project is to have Navitia2 progressively deployed in a more simple and robust
way, and on any kind of platform, offering:
- Easy and fast deployment on a development platform,
- Running of complete or partial test scenarios on a development platform or on any dedicated platform,
  giving developpers unprecedented flexibility to run customized tests more efficiently,
- More easy and robust deployment on staging or production platforms, especially for customers running
  their own platforms, but also for partners seeking unmanaged self deployment,
- Build automation of platforms (see Creation below) that create  
  
Docker images are architectured in a way such that updating Navitia to the latest version is as simple
as replacing old images with new ones and restarting them.
For this to be possible, all data are kept in folder external to docker containers but accessed
via folder bindings (known to docker as 'volumes')

# Creation
Navitia in docker containers can follow different configurations (named platforms in docker_navitia source).
There are currently 2 configurations of docker images:
- monolythic: all components and services are in a single image. This simple configuration is
  ideal for development and tests purposes.
- composed: each component fits in an image. There are 4 components (Ed, Tyr, Engine, WS),
  each corresponding to an image.
  
Other configurations can be developed. This can be done by creating a new platform file, new Dockerfile 
and supervisord.conf files, then instanciating a new BuildDockerCompose object with apropriate ports, 
volumes and links before launching build process then python-fabric installation process.
   
# TODO naming, images vs containers

# Limitations
The current version of this project only allows for one instance of navitia2 (simle or composed) to run
on a machine (real or virtual). Future development will allow to run multiple instances on a single machine,
a use case that can be useful for Jenkins for example.
