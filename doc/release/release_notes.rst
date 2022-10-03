..
    :copyright: Copyright (c) 2022 ftrack

.. _release/release_notes:

*************
Release Notes
*************

.. release:: upcoming

    .. change:: change
        :tags: maya

        Implemented use of dynamic widget group box.


    .. change:: change
        :tags: maya

        Changed exporter options widgets to properly use dynamic widget combobox functionality.


    .. change:: change
        :tags: options

        Aligned with QT plugin/widget refactorization.


    .. change:: fix
        :tags: nuke

        Changed wrong usage of nuke publisher finalizer, removed unused finalizers.


    .. change:: new
        :tags: nuke

        Rename default plugins to native or generic, remove test code from finalizers, relabel finalizers.


    .. change:: new
        :tags: nuke

        Specialise camera and geometry collectors in nuke, add validators


    .. change:: new
        :tags: nuke

        Maya model exporter crashes


    .. change:: new
        :tags: nuke

        Added node existance check to collector


    .. change:: new
        :tags: nuke

        Fix Movie publisher validator


    .. change:: new
        :tags: nuke

        Renamed option supported_file_formats


    .. change:: new
        :tags: nuke

        Code style fix


    .. change:: new
        :tags: nuke

        Set mp4v as default movie codec; Added reviewable format and codec to options


    .. change:: new
        :tags: nuke

        Add codec selection on Nuke movie exporter


    .. change:: new
        :tags: nuke

        Aligned movie loader name with publisher


    .. change:: new
        :tags: nuke

        Updated reported selection label


    .. change:: new
        :tags: nuke

        Renamed Nuke nuke_default_publisher_collector to nuke_node_publisher_collector plugin and definition names


    .. change:: new
        :tags: nuke

        Renamed Nuke nuke_default_publisher_collector to nuke_node_publisher_collector plugin and definition names

    .. change:: change
        :tags: nuke

        Added as optional to nodes publisher

    .. change:: new
        :tags: nuke

        Add thumbnail to Nuke SCENE Publisher

    .. change:: new
        :tags: nuke

        Re-adding all Nuke RC5 plugins to definitions

    .. change:: new
        :tags: nuke

        Add common collector for image sequence and movie publisher, also fix movie publisher on mac m1

.. release:: 1.0.1
    :date: 2022-08-01

    .. change:: new

        Initial release

