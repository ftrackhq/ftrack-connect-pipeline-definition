# Definitions

-   \* mark a mandatory field
-   \<\> a variable
-   \<\[, \...\]\> example of potential arguments of the variable

## Package

Defines what a package is, based on where to find it and what components
provides.

> {
>
> :   -   \"name\": \"\<display name \[Animation, Modeling, \...\]\>\",
>
>     -   \"type\": \"\<asset Type \[modelPkg, rigPkg, \...\]\>\",
>
>     -   
>
>         \"context\": \[
>
>         :   -   \"\<context type \[Task, Modeling, \...\]\>\"
>
>         \],
>
>     -   
>
>         \"components\": \[
>
>         :   
>
>             \* {
>
>             :   \"name\": \"\<component name\>\", \"file_type\":
>                 \[\"\<component type \[png, mb, \...\]\>\"\] }
>
>         \]
>
> }

## Plugin

All the fields are optional apart from plugin one. Defines the plugin
which will be called.

> {
>
> :   \"name\": \"\<plugin display name\>\", \"description\": \"\<plugin
>     description \>\", \* \"plugin\": \"\<plugin id used to execute the
>     process\>\", \"widget\": \"\<widget id used to render the process
>     ui\>\", \"visible\": \"\<bool\>\", \"editable\": \"\<bool\>\",
>     \"disabled\": \"\<bool\>\", \"options\": { \"\<key\>\":
>     \"\<value\>\", }
>
> }

## Package Publisher

Defines what components to publish and how.

> {
>
> :   -   \"name\": \"\<display name\>\",
>
>     -   \"package\": \"\<asset Type \[modelPkg, rigPkg, \...\]\>\",
>
>     -   \"host_type\": \"\<host Type \[maya, nuke, \...\]\>\",
>
>     -   \"ui_type\": \"\<ui Type \[qt, js, \...\]\>\",
>
>     -   
>
>         \"context\": \[
>
>         :   -   \"\<context plugin Type\>\"
>
>         \],
>
>     -   
>
>         \"components\": {
>
>         :   -   
>
>                 \"\<component name \[main, color, \...\]\>\": {
>
>                 :   -   
>
>                         \"collect\": \[
>
>                         :   -   \"\<collect plugin Type
>                                 \[from_selection, from_set,
>                                 from_filesystem, \...\]\>\",
>
>                         \],
>
>                     -   
>
>                         \"validate\": \[
>
>                         :   -   \"\<validate plugin Type
>                                 \[non_mailfold, non_null, \...\]\>\",
>
>                         \],
>
>                     -   
>
>                         \"exporter\": \[
>
>                         :   -   \"\<exporter plugin Type \[mayabinary,
>                                 nukefile, images, \...\]\>\",
>
>                         \]
>
>                 }
>
>         },
>
>     -   
>
>         \"publish\": \[
>
>         :   -   \"\<publish plugin Type \[components, metadata,
>                 \...\]\>\"
>
>         \]
>
> }

## Package Loader

Defines how to re load published packages.

> {
>
> :   -   \"name\": \"\<display name\>\",
>     -   \"host_type\": \"\<host Type \[maya, nuke, \...\]\>\",
>     -   \"ui_type\": \"\<ui Type \[qt, js, \...\]\>\",
>
>     \* \"context\": \[
>
>     :   -   \"\<context plugin Type\>\"
>
>     \], \* \"components\": \[ \* \"\<load plugin Type \[geometry,
>     textures\]\>\" \], \"post\": \[ \"\<post import plugin
>     Type\[set_layout, attach_shaders, \...\] \>\" \]
>
> }