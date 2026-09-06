# Referencia de la API de GML — variables y structs incorporados

> Runtime **2026.0.0.23**. 210 variables y 33 structs.

## Variables incorporadas

| Variable | Tipo | Ámbito | Lectura | Escritura | Descripción |
|---|---|---|---|---|---|
| `alarm` | `Array[Real]` | instancia | sí | sí | This 1 dimensional array is used to get the current value for any alarms that the instance may have, or it can be used to set those alarms. There are twelve ala |
| `application_surface` | `Id.Surface` | global | sí | no | This global scope, built-in variable can be used to access the application surface using any of the surface functions. This surface is permanently available and |
| `argument` | `ArgumentIdentity` | global | sí | sí |  |
| `argument0` | `ArgumentIdentity` | global | sí | sí |  |
| `argument1` | `ArgumentIdentity` | global | sí | sí |  |
| `argument10` | `ArgumentIdentity` | global | sí | sí |  |
| `argument11` | `ArgumentIdentity` | global | sí | sí |  |
| `argument12` | `ArgumentIdentity` | global | sí | sí |  |
| `argument13` | `ArgumentIdentity` | global | sí | sí |  |
| `argument14` | `ArgumentIdentity` | global | sí | sí |  |
| `argument15` | `ArgumentIdentity` | global | sí | sí |  |
| `argument2` | `ArgumentIdentity` | global | sí | sí |  |
| `argument3` | `ArgumentIdentity` | global | sí | sí |  |
| `argument4` | `ArgumentIdentity` | global | sí | sí |  |
| `argument5` | `ArgumentIdentity` | global | sí | sí |  |
| `argument6` | `ArgumentIdentity` | global | sí | sí |  |
| `argument7` | `ArgumentIdentity` | global | sí | sí |  |
| `argument8` | `ArgumentIdentity` | global | sí | sí |  |
| `argument9` | `ArgumentIdentity` | global | sí | sí |  |
| `argument_count` | `Real` | global | sí | no | This read-only variable holds the number of "arguments" that are passed through to a script function or a method. |
| `argument_relative` ⚠️obsoleta | `Real` | global | sí | no |  |
| `async_load` | `Id.DsMap` | global | sí | no | This global variable holds a DS Map when used in the Asynchronous Events, and an invalid DS Map handle (-1) at all other times. |
| `background_color` ⚠️obsoleta | `Constant.Color` | global | sí | sí |  |
| `background_colour` ⚠️obsoleta | `Constant.Color` | global | sí | sí |  |
| `background_showcolor` ⚠️obsoleta | `Bool` | global | sí | sí |  |
| `background_showcolour` ⚠️obsoleta | `Real` | global | sí | sí |  |
| `bbox_bottom` | `Real` | instancia | sí | no | This read-only variable returns the y position (within the room) of the bottom of the bounding box for the instance, where the bounding box is defined by the ma |
| `bbox_left` | `Real` | instancia | sí | no | This read-only variable returns the position (along the x-axis) within the room of the left hand bounding box for the instance, where the bounding box is define |
| `bbox_right` | `Real` | instancia | sí | no | This read-only variable returns the position within the room (along the x-axis) of the right hand side of the bounding box for the instance, where the bounding  |
| `bbox_top` | `Real` | instancia | sí | no | This read-only variable returns the position within the room (along the y-axis) of the top of the bounding box for the instance, where the bounding box is defin |
| `browser_height` | `Real` | global | sí | no | This variable holds the height (in pixels) of the browser the game is being run in. If no browser is present then the window size is returned. |
| `browser_width` | `Real` | global | sí | no | This variable holds the width (in pixels) of the browser the game is being run in. If no browser is present then the window size is returned. |
| `cache_directory` | `String` | global | sí | no | This can be used to return the cache directory created for your game (including trailing "\"). This directory will hold files and can be accessed while the game |
| `caption_health` ⚠️obsoleta | `String` | global | sí | sí |  |
| `caption_lives` ⚠️obsoleta | `String` | global | sí | sí |  |
| `caption_score` ⚠️obsoleta | `String` | global | sí | sí |  |
| `collision_space` | `colspace` | instancia | sí | no | This read-only variable returns the collision space the instance is in. |
| `current_day` | `Real` | global | sí | no | This read-only variable will return the day as a value from 1 to 31, depending on the month. |
| `current_hour` | `Real` | global | sí | no | This read-only variable will return the hour that corresponds to the current moment based on the default time zone for the system (i.e.: local time). You can ch |
| `current_minute` | `Real` | global | sí | no | This read-only variable will return the minutes that correspond to the current moment. |
| `current_month` | `Real` | global | sí | no | This read-only variable returns the current month as a numeric value where 1 is January and 12 is December. |
| `current_second` | `Real` | global | sí | no | This read-only variable will return the seconds that correspond to the current moment. |
| `current_time` | `Real` | global | sí | no | This read-only variable will return the number of milliseconds that have passed since the game was started. |
| `current_weekday` | `Real` | global | sí | no | This read-only variable will return the weekday as a value, where Sunday is 0 and Saturday is 6. |
| `current_year` | `Real` | global | sí | no | This read-only variable will return the current year. |
| `cursor_sprite` | `Asset.GMSprite` | global | sí | sí | Setting this variable will instruct GameMaker to use the designated sprite as a cursor (basically setting it to the current mouse x/y position every step). The  |
| `debug_mode` | `Bool` | global | sí | no | This read-only variable returns true when the game is being played in debug mode and false when being played as normal. |
| `delta_time` | `Real` | global | sí | no | This variable returns the frame delta time, which is the time difference between the previous frame and the current frame. This value is in microseconds, where  |
| `depth` | `Real` | instancia | sí | sí | This built-in variable stores the depth of the instance. |
| `direction` | `Real` | instancia | sí | sí | This built-in variable stores the direction of the instance. |
| `display_aa` | `Real` | global | sí | no | This read-only variable holds the different levels of AA that the device running the game can display. |
| `drawn_by_sequence` | `Bool` | instancia | sí | sí | This is a built-in variable that is part of the instance variables created for every object instance in your game. This can be changed at any time but will only |
| `error_last` ⚠️obsoleta | `Bool` | global | sí | sí |  |
| `error_occurred` ⚠️obsoleta | `Bool` | global | sí | sí |  |
| `event_action` ⚠️obsoleta | `Real` | global | sí | no |  |
| `event_data` | `Id.DsMap` | global | sí | no | This variable is global in scope and is used to hold a DS Map when used in the Gesture Events, and -1 at all other times. The actual contents of the DS map will |
| `event_number` | `Constant.EventNumber` | instancia | sí | no | This read-only variable returns the number of the event currently being called, where the number is actually referring to the "sub event" of the event, i.e.: fo |
| `event_object` | `Asset.GMObject` | instancia | sí | no | This read-only variable returns the object index of the instance which is running the event being checked. |
| `event_type` | `Constant.EventType` | instancia | sí | no | This read-only variable returns the type of event currently being executed. |
| `font_texture_page_size` | `Real` | global | sí | sí | This built-in variable can be used to either get or set the texture page size when using the function font_add(). On adding a font using that function, GameMake |
| `fps` | `Real` | global | sí | no | This read-only variable holds the current fps as an integer value. |
| `fps_real` | `Real` | global | sí | no | This read-only variable holds the current real fps as an integer value. |
| `friction` | `Real` | instancia | sí | sí | This built-in variable stores the friction of the instance. |
| `game_display_name` | `String` | global | sí | no | This read-only variable returns the display name of your game for the target platform, as set in the Game Options. |
| `game_id` ⚠️obsoleta | `Real` | global | sí | no | This read-only variable returns the unique identifier for the game you have created. You can use this if you need a unique file name, or anything else that need |
| `game_project_name` | `String` | global | sí | no | This read-only variable returns the display name of your game for the target platform in a "save-friendly" format for the target platform. If the display name c |
| `game_save_id` | `String` | global | sí | no | This read-only variable will return the full path ID of the directory that is used by your game to save files to. This directory may or may not be visible to ot |
| `gamemaker_pro` ⚠️obsoleta | `Bool` | global | sí | no |  |
| `gamemaker_registered` ⚠️obsoleta | `Bool` | global | sí | no |  |
| `gravity` | `Real` | instancia | sí | sí | gravity is one of the built-in variables all instances have and, when set, will apply a constant force in the gravity_direction of the instance, influencing bot |
| `gravity_direction` | `Real` | instancia | sí | sí | gravity_direction is one of the built-in properties all instances have and can be used to set the direction of movement when the instance's gravity is greater t |
| `health` ⚠️obsoleta | `Real` | global | sí | sí |  |
| `hspeed` | `Real` | instancia | sí | sí | hspeed is one of the built-in properties that all instances have and defines the horizontal movement speed (along the x-axis) of the instance in pixels per step |
| `iap_data` ⚠️obsoleta | `Undefined` | global | sí | no |  |
| `id` | `Id.Instance` | instancia | sí | no | This read-only variable holds the unique identifying number for the instance. Every instance that you create - whether through code or by adding them to a room  |
| `image_alpha` | `Real` | instancia | sí | sí | This variable is used to get or to set the alpha value for the sprite. Alpha is always calculated as a value between 0 and 1 where 0 is completely transparent a |
| `image_angle` | `Real` | instancia | sí | sí | This value sets the angle (rotation) of the sprite and is measured in degrees, with the right being 0º, up being 90º, left being 180º and down being 270º. Set t |
| `image_blend` | `Constant.Color` | instancia | sí | sí | This variable controls the "tinting" of the instance sprite and the default value is -1 (but can also be c_white). Any other value (including internal colour co |
| `image_index` | `Real` | instancia | sí | sí | This built-in variable holds the current frame of the instance's animation. |
| `image_number` | `Real` | instancia | sí | no | This read-only variable can be used to get the number of sub-images in a sprite that has been assigned to an instance (if you need the number of sub-images for  |
| `image_speed` | `Real` | instancia | sí | sí | This variable determines the speed in which GameMaker will cycle through the sub-images for the current instance sprite. The speed value given is a multiplier,  |
| `image_xscale` | `Real` | instancia | sí | sí | This value sets the horizontal scaling applied to the sprite that has been assigned to the current instance. A scale of 1 indicates no scaling (1:1), smaller va |
| `image_yscale` | `Real` | instancia | sí | sí | This value sets the vertical scaling (along the y-axis) applied to the sprite that has been assigned to the current instance. A scale of 1 indicates no scaling  |
| `in_collision_tree` | `Bool` | instancia | sí | no |  |
| `in_sequence` | `Bool` | instancia | sí | sí | This is a built-in variable that is part of the instance variables created for every object instance in your game. If the instance is being controlled by a sequ |
| `instance_count` | `Real` | global | sí | no | With this read-only variable you can get a count of all active instances that are in the room. This will include the instance running the code, but does not inc |
| `instance_id` | `Array[Id.Instance]` | global | sí | no | This read-only array holds all the ids of every active instance within the room. This means that if you have used any of the Instance Deactivate functions those |
| `keyboard_key` | `Constant.VirtualKey` | global | sí | sí | With this variable you can get the keycode of the key that is currently being pressed and it will return 0 if no key is being pressed when the check is done. |
| `keyboard_lastchar` | `String` | global | sí | sí | This variable stores a string of the last key pressed. This variable is not read-only and you can change it, for example to set it to "" (an empty string) if yo |
| `keyboard_lastkey` | `Constant.VirtualKey` | global | sí | sí | This variable refers to the value that keyboard_key was in the previous frame, returning the keycode of that key (all standard keycode constants are returned).  |
| `keyboard_string` | `String` | global | sí | sí | This variable holds a string containing the last (at most) 1024 characters typed on the keyboard. This string will only contain printable characters typed, but  |
| `layer` | `Id.Layer` | instancia | sí | sí | This built-in variable is created for every instance in a room and contains the layer ID value of the layer that the instance is assigned to. |
| `lives` ⚠️obsoleta | `Real` | global | sí | sí |  |
| `managed` | `Bool` | global | sí | no | This read-only variable indicates whether the object is managed by the rollback multiplayer system or not. |
| `mask_index` | `Asset.GMSprite` | instancia | sí | sí | This variable holds the sprite_index used as the instance's collision mask, or -1 if no mask has been assigned and its actual sprite_index is used for collision |
| `mouse_button` | `Constant.MouseButton` | global | sí | sí | This read-only variable returns the mouse button that is currently being pressed (currently, as in, this step) and can return any of the special mouse constants |
| `mouse_lastbutton` | `Constant.MouseButton` | global | sí | sí | This variable returns the last mouse button that was pressed and can return any of the special mouse constants except mb_any (you may also set this variable to  |
| `mouse_x` | `Real` | global | sí | no | This read-only variable returns the current x axis position of the mouse within the room. |
| `mouse_y` | `Real` | global | sí | no | This read-only variable returns the current y axis position of the mouse within the room. |
| `object_index` | `Asset.GMObject` | instancia | sí | no | This read-only variable returns the index of the object that the instance has been created from. This is not the same as the object name, which is a string and  |
| `on_ui_layer` | `Bool` | instancia | sí | no | This built-in variable can be read to find out if the instance is currently on a UI layer or not. |
| `os_browser` | `Constant.BrowserType` | global | sí | no | This read-only variable holds one of various constants that GameMaker has to tell you which browser you are currently running the game in (if any). |
| `os_device` ⚠️obsoleta | `Constant.DeviceType` | global | sí | no | This read-only variable holds one of various constant values to tell you which device you are currently running the game on. Note this variable is deprecated in |
| `os_type` | `Constant.OperatingSystem` | global | sí | no | This read-only variable holds one of various constant GameMaker has to tell you which operating system the game has been created for. Note that this is not nece |
| `os_version` | `Real` | global | sí | no | This variable will tell you the version number for the OS that is running your game. For example, if you are running it on Windows 10, os_version will be equal  |
| `path_endaction` | `Constant.PathAction` | instancia | sí | sí | This variable can be used to get or to change the reaction of an instance when it reaches the end of the current path. Normally you would set this when you star |
| `path_index` | `Asset.GMPath` | global | sí | no | The variable path_index is a read-only variable that holds the handle for a given path asset that has been assigned to an instance using the path_start() functi |
| `path_orientation` | `Real` | instancia | sí | sí | This variable holds the current orientation of the path that has been assigned to the instance when the function path_start() was called. When a path is created |
| `path_position` | `Real` | instancia | sí | sí | This function can be used to get or set the position of an instance along a path. The value is normalised from 0 - 1, so if you set it to, for example, 0.5, the |
| `path_positionprevious` | `Real` | instancia | sí | sí | This variable can be used to get or to set the position of an instance along its current path in the previous step, and is a normalised value between 0 and 1 i. |
| `path_scale` | `Real` | instancia | sí | sí | This value can be used to get or to set the scale of the currently assigned path for the instance (as set by the function path_start()) with a default value of  |
| `path_speed` | `Real` | instancia | sí | sí | You can use this function to get or to set the speed of a path after it has been started using the function path_start(). You can use negative values to signify |
| `persistent` | `Bool` | instancia | sí | sí | This variable can be read to find out if the instance is flagged as persistent or not, or it can used to set persistence to true (persistent) or false (not pers |
| `phy_active` | `Bool` | instancia | sí | sí | This variable controls whether or not the instance is currently "active". Setting it to false will prevent the instance from participating in the physics world, |
| `phy_angular_damping` | `Real` | instancia | sí | sí | This variable can be used to set the angular damping of the instance, or it can be used to get the current angular damping. The damping is the amount of "resist |
| `phy_angular_velocity` | `Real` | instancia | sí | sí | This variable can be used to set the angular velocity of the instance, or it can be used to get the current angular velocity, in degrees per second and the valu |
| `phy_bullet` | `Bool` | instancia | sí | sí | This variable defines whether or not the instance is extremely fast moving (for example a bullet). The default value is false but if set to true this tells Game |
| `phy_col_normal_x` | `Real` | instancia | sí | no | This read-only variable returns the x component of the collision normal corresponding to the phy_collision_x array value. For each contact point there is an ass |
| `phy_col_normal_y` | `Real` | instancia | sí | no | This read-only variable returns the y component of the collision normal corresponding to the phy_collision_y array value. For each contact point there is an ass |
| `phy_collision_points` | `Real` | instancia | sí | no | This read-only variable returns the number of points of collision detected between the two objects in the collision. |
| `phy_collision_x` | `Array[Real]` | instancia | sí | no | This read-only array returns the x position of all points detected in a collision between two physics-enabled instances. |
| `phy_collision_y` | `Array[Real]` | instancia | sí | no | This read-only array returns the y position of all points detected in a collision between two physics-enabled instances. |
| `phy_com_x` | `Real` | instancia | sí | no | This read-only variable will return the x position of the instance's center of mass. This is calculated automatically based on the density, inertia and mass of  |
| `phy_com_y` | `Real` | instancia | sí | no | This read-only variable will return the y position of the instance's center of mass. This is calculated automatically based on the density, inertia and mass of  |
| `phy_dynamic` | `Bool` | instancia | sí | no | A dynamic instance is one that is fully simulated within the physics world and this read-only variable will return true if the instance being checked is fully s |
| `phy_fixed_rotation` | `Bool` | instancia | sí | sí | This variable can be used to set whether or not the instance can be affected by rotational forces (default is false). If this is set to true, no external force  |
| `phy_inertia` | `Real` | instancia | sí | no | This variable holds the inertia for a physics-enabled instance. Inertia is the measure of how hard it is to make something start or stop moving, so the lower th |
| `phy_kinematic` | `Bool` | instancia | sí | no | This read-only variable will return true if the instance is classed as being a kinematic object, or false if it is not. A kinematic instance is one that has inf |
| `phy_linear_damping` | `Real` | instancia | sí | sí | This variable can be used to set the linear damping of the instance, or it can be used to get the current linear damping. The damping is the amount of "resistan |
| `phy_linear_velocity_x` | `Real` | instancia | sí | sí | This variable can be used to get or change the x component of the instance's linear velocity vector and is defined in pixels per second (for pixels per step, se |
| `phy_linear_velocity_y` | `Real` | instancia | sí | sí | This variable can be used to get or change the y component of the instance's linear velocity vector and is defined in pixels per second (for pixels per step, se |
| `phy_mass` | `Real` | instancia | sí | no | This read-only variable returns the mass of the instance in kilograms. This value is calculated automatically based on the surface area of the assigned fixtures |
| `phy_position_x` | `Real` | instancia | sí | sí | This variable can be used to get (or to set) the x position of the instance within the game room physics world. Please note that the physics world may present e |
| `phy_position_xprevious` | `Real` | instancia | sí | no | This variable can be used to get (or to set) the previous x position of the instance within the game room physics world. This is the position of the instance wi |
| `phy_position_y` | `Real` | instancia | sí | sí | This variable can be used to get (or to set) the y position of the instance within the game room physics world. Please note that the physics world may present e |
| `phy_position_yprevious` | `Real` | instancia | sí | no | This variable can be used to get (or to set) the previous y position of the instance within the game room physics world. This is the position of the instance wi |
| `phy_rotation` | `Real` | instancia | sí | sí | This variable can be used to get (or to set) the angle of the instance's fixture in degrees, similar to setting or getting the image_angle. However, note that i |
| `phy_sleeping` | `Bool` | instancia | sí | no | This read-only variable returns whether or not the instance is currently "sleeping" (true) or not (false), A "sleeping" instance is one that is not actively eng |
| `phy_speed` | `Real` | instancia | sí | no | This read-only variable returns the current speed of the physics-enabled instance, defined in pixels per step. Should you need to change this value, you must do |
| `phy_speed_x` | `Real` | instancia | sí | sí | This variable can be used to get or change the x component of the instance's linear speed vector and is defined in pixels per step (for pixels per second, see p |
| `phy_speed_y` | `Real` | instancia | sí | sí | This variable can be used to get or change the y component of the instance's linear speed vector and is defined in pixels per step (for pixels per second, see p |
| `player_avatar_sprite` | `Asset.GMSprite` | instancia | sí | no | A sprite of the avatar associated with this player in Opera GX, for rollback networking. |
| `player_avatar_url` | `String` | instancia | sí | no | The URL to the avatar associated with this player in Opera GX, for rollback networking. |
| `player_id` | `Real` | instancia | sí | no | This identifies which player the instance belongs to in the rollback networking system. |
| `player_local` | `Bool` | instancia | sí | no | This identifies if this instance belongs to the local player in the rollback networking system. |
| `player_type` | `String` | instancia | sí | no | This identifies if this instance belongs a Guest or User account in the rollback networking system. |
| `player_user_id` | `String` | instancia | sí | no | This is the user id in Opera GX in the rollback networking system. |
| `program_directory` | `String` | global | sí | no | This will return the directory where the game executable is stored. However this may not always be useful, particularly as some devices run the exe from a *.zip |
| `rollback_api_server` | `String` | global | sí | no | This global variable contains the gx games API url |
| `rollback_confirmed_frame` | `Real` | global | sí | no | This global variable contains the frame number for which we have confirmed input for all players |
| `rollback_current_frame` | `Real` | global | sí | no | This global variable contains the network tick and can be used in rollback networking instead of wall clock time |
| `rollback_event_id` | `Real` | global | sí | no | This global variable contains the last event id that was fired |
| `rollback_event_param` | `Asset.GMObject` | global | sí | no | This global variable contains a struct with parameters for the last event that was fired |
| `rollback_game_running` | `Bool` | global | sí | no | This global variable contains the flag if the game is currently running |
| `room` | `Asset.GMRoom` | global | sí | sí | This variable holds the room index for the current room that your game is running. |
| `room_caption` ⚠️obsoleta | `String` | global | sí | sí |  |
| `room_first` | `Asset.GMRoom` | global | sí | no | This read-only variable returns the index of the very first room in the game (this is defined by the order in which the rooms appear in the Room Manager and not |
| `room_height` | `Real` | global | sí | sí | This variable holds the height of the current room in pixels. You can change this variable to change the height of the room at any time, and changes will be app |
| `room_last` | `Asset.GMRoom` | global | sí | no | This read-only variable returns the index of the very last room in the game (this is defined by the order in which the rooms appear in the Room Manager and not  |
| `room_persistent` | `Bool` | global | sí | sí | This variable can be used to get and to set the persistent flag for the current room. If set to true the room is considered persistent, in which case each time  |
| `room_speed` ⚠️obsoleta | `Real` | global | sí | sí |  |
| `room_width` | `Real` | global | sí | sí | This variable holds the width of the current room in pixels. You can change this variable to change the width of the room at any time. |
| `score` ⚠️obsoleta | `Real` | global | sí | sí |  |
| `sequence_instance` | `Struct.SequenceInstance` | instancia | sí | no | This is a built-in variable that is part of the instance variables created for every object instance in your game. If the instance is being controlled by a sequ |
| `show_health` ⚠️obsoleta | `Bool` | global | sí | sí |  |
| `show_lives` ⚠️obsoleta | `Bool` | global | sí | sí |  |
| `show_score` ⚠️obsoleta | `Bool` | global | sí | sí |  |
| `solid` | `Bool` | instancia | sí | sí | An instance can be flagged as solid through the object properties in the Object Editor, or by changing the value of this built-in variable. If solid is set to t |
| `speed` | `Real` | instancia | sí | sí | This built-in variable stores the speed of the instance in pixels per step. |
| `sprite_height` | `Real` | instancia | sí | no | This read-only variable returns the height of the sprite that has been assigned to the instance. This height is returned in pixels and will be dependent on the  |
| `sprite_index` | `Asset.GMSprite` | instancia | sí | sí | This variable holds the index of the current sprite for the instance, or -1 if the instance has no sprite associated with it. |
| `sprite_width` | `Real` | instancia | sí | no | This read-only variable returns the width of the sprite that has been assigned to the instance. This width is returned in pixels and will be dependent on the im |
| `sprite_xoffset` | `Real` | instancia | sí | no | This read-only variable returns the local xoffset (the x component of the origin as defined in the sprite editor) of the sprite that has been assigned to the in |
| `sprite_yoffset` | `Real` | instancia | sí | no | This read-only variable returns the local yoffset (the y component of the origin as defined in the sprite editor) of the sprite that has been assigned to the in |
| `temp_directory` | `String` | global | sí | no | This can be used to return the temporary directory created for your game each time it is run (including trailing "\""). This directory will hold files and can b |
| `timeline_index` | `Asset.GMTimeline` | instancia | sí | sí | This variable holds the index of the time line currently associated with the instance. You can set this to a particular time line to use that one, or set it to  |
| `timeline_loop` | `Bool` | instancia | sí | sí | This variable will return whether the time line is looping (true) or not (false). You can change this variable to switch looping on or off and it works with a n |
| `timeline_position` | `Real` | instancia | sí | sí | This variable holds the current position (moment) a time line is currently at. You can change this value to skip parts of the time line, or to repeat parts or t |
| `timeline_running` | `Bool` | instancia | sí | sí | This variable holds current state of the assigned time line and will return true if it is running and false if it is not. You can also set this variable to eith |
| `timeline_speed` | `Real` | instancia | sí | sí | This built-in variable holds the speed of the timeline currently assigned to the instance. |
| `view_angle` ⚠️obsoleta | `Array[Real]` | global | no | no | Reserved, obsolete variable (won't behave correctly, do not use). |
| `view_camera` | `Array[Id.Camera]` | global | sí | sí | This array holds the unique camera ID assigned to the given viewport, and can be set to a new camera or read to get the current camera, returning -1 if no camer |
| `view_current` | `Real` | global | sí | no | This read-only variable is only valid in the Draw Event and returns the current viewport being rendered. The return value will change during the draw event when |
| `view_enabled` | `Bool` | global | sí | sí | This variable controls whether any viewports that are visible within the room are enabled or not. If you have viewports set to visible and then disable this opt |
| `view_hborder` ⚠️obsoleta | `Array[Real]` | global | no | no | Reserved, obsolete variable (won't behave correctly, do not use). |
| `view_hport` | `Array[Real]` | global | sí | sí | This variable can be used to get or to set the height of the specified viewport. The height of the viewport (or combined viewports if more than one are active)  |
| `view_hspeed` ⚠️obsoleta | `Array[Real]` | global | no | no | Reserved, obsolete variable (won't behave correctly, do not use). |
| `view_hview` ⚠️obsoleta | `Array[Real]` | global | no | no | Reserved, obsolete variable (won't behave correctly, do not use). |
| `view_object` ⚠️obsoleta | `Array[Real]` | global | no | no | Reserved, obsolete variable (won't behave correctly, do not use). |
| `view_surface_id` | `Array[Id.Surface]` | global | sí | sí | With this variable you can set the contents of a given viewport to draw to a surface, or get the current surface if one has been assigned to a viewport. |
| `view_vborder` ⚠️obsoleta | `Array[Real]` | global | no | no | Reserved, obsolete variable (won't behave correctly, do not use). |
| `view_visible` | `Array[Bool]` | global | sí | sí | This variable can be used to find out if a particular viewport is currently visible or not. You can also set this variable to effectively turn "on" or "off" a v |
| `view_vspeed` ⚠️obsoleta | `Array[Real]` | global | no | no | Reserved, obsolete variable (won't behave correctly, do not use). |
| `view_wport` | `Array[Real]` | global | sí | sí | This variable can be used to get or to set the width of the specified viewport. The width of the viewport (or combined viewports if more than one are active) de |
| `view_wview` ⚠️obsoleta | `Array[Real]` | global | no | no | Reserved, obsolete variable (won't behave correctly, do not use). |
| `view_xport` | `Array[Real]` | global | sí | sí | With this built-in array you can get or set the x position of the given viewport. The viewport is the area on the screen where the view is drawn, and you can ha |
| `view_xview` ⚠️obsoleta | `Array[Real]` | global | no | no | Reserved, obsolete variable (won't behave correctly, do not use). |
| `view_yport` | `Array[Real]` | global | sí | sí | With this built-in array you can get or set the y position of the given viewport. The viewport is the area on the screen where the view is drawn, and you can ha |
| `view_yview` ⚠️obsoleta | `Array[Real]` | global | no | no | Reserved, obsolete variable (won't behave correctly, do not use). |
| `visible` | `Bool` | global | sí | sí | An instance can be flagged as visible or not by setting this variable to true (visible) or false (invisible). |
| `vspeed` | `Real` | instancia | sí | sí | vspeed is one of the built-in properties that all instances have and defines the vertical movement speed (along the y-axis) of the instance in pixels per step.  |
| `wallpaper_config` | `Asset.GMObject` | global | sí | no | This global variable contains a struct with parameters for the last Wallpaper Config event that was fired. |
| `webgl_enabled` | `Bool` | global | sí | no | This read-only variable will return whether WebGL is enabled (true) or not (false) for your game. It will only work for those games running through a browser (i |
| `working_directory` | `String` | global | sí | no | working_directory can actually return two different values depending on what you are using it for. If you are writing a file to disk, working_directory points t |
| `x` | `Real` | instancia | sí | sí | The x value of an instance is the horizontal position in the current room, measured in pixels. This value can be either 0, positive or negative, where 0 is the  |
| `xprevious` | `Real` | instancia | sí | sí | This built-in variable returns the previous x position for the instance. This variable will be set just before the start of the begin step event but it can also |
| `xstart` | `Real` | instancia | sí | sí | This variable stores the initial x position of the instance when it is first created in the room. This is not a read-only variable and can be set as well as rea |
| `y` | `Real` | instancia | sí | sí | The y value of an instance is the vertical position in the current room, measured in pixels. This value can be either 0, positive or minus, where 0 is the top o |
| `yprevious` | `Real` | instancia | sí | sí | This built-in variable returns the previous y position for the instance. This variable will be set to the current x position just before the start of the begin  |
| `ystart` | `Real` | instancia | sí | sí | This variable stores the initial y position of the instance when it is first created in the room. This is not a read-only variable and can be set as well as rea |

## Structs incorporados


### `ActiveTrack`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `activeTracks` | `Array[Struct.Track]` | sí | no | READ-ONLY This is an array of evaluation structs for each parameter track that the asset track contains. The contents of each struct in the array are listed on  |
| `matrix` | `Array` | sí | sí | The transformation matrix of the track within the parent track's frame of reference (all asset track types). |
| `posx` | `Real` | sí | sí | The position of the asset in the sequence along the X axis for the track (all asset track types). |
| `posy` | `Real` | sí | sí | The position of the asset in the sequence along the Y axis for the track (all asset track types). |
| `scalex` | `Real` | sí | sí | The scale of the asset in the sequence along the X axis for the track (group, particle system, instance, sequence, text and sprite asset track types). |
| `scaley` | `Real` | sí | sí | The scale of the asset in the sequence along the Y axis for the track (group, particle system, instance, sequence, text and sprite asset track types). |
| `xorigin` | `Real` | sí | sí | The X origin of the asset for the track (group, particle system, instance, sequence, text and sprite asset track types). |
| `yorigin` | `Real` | sí | sí | The Y origin of the asset for the track (group, particle system, instance, sequence, text and sprite asset track types). |
| `gain` | `Real` | sí | sí | The gain of the track, which is the emitter gain. |
| `pitch` | `Real` | sí | sí | The pitch of the track, which is the emitter pitch. |
| `falloffRef` | `Real` | sí | sí | The audio emitter's falloff reference distance. |
| `falloffMax` | `Real` | sí | sí | The audio emitter's falloff maximum distance. |
| `falloffFactor` | `Real` | sí | sí | The audio emitter's falloff factor. |
| `width` | `Real` | sí | sí |  |
| `height` | `Real` | sí | sí |  |
| `imageindex` | `Real` | sí | sí | The image index for the asset on the track in the sequence. |
| `imagespeed` | `Real` | sí | sí | The image speed for the asset on the track in the sequence. |
| `colorMultiply` | `Array` | sí | sí | The color multiply value for the asset on the track in the sequence at the current playhead position (sprite, instance and sequence tracks). This value will be  |
| `colourMultiply` | `Array` | sí | sí | The colour multiply value for the asset on the track in the sequence at the current playhead position (sprite, instance and sequence tracks). This value will be |
| `emitterIndex` | `Id.AudioEmitter` | sí | sí | READ-ONLY The index of the audio emitter used by this track. |
| `track` | `Struct.Track` | sí | sí | READ-ONLY The Track Struct that this track is based on. |
| `parent` | `Struct.SequenceInstance` | sí | sí | READ-ONLY The parent sequence instance ID for the track. |
| `frameSizeX` | `Real` | sí | sí | The horizontal size of the text frame. |
| `frameSizeY` | `Real` | sí | sí | The vertical size of the text frame. |
| `characterSpacing` | `Real` | sí | sí | The character spacing value. |
| `lineSpacing` | `Real` | sí | sí | The line spacing value. |
| `paragraphSpacing` | `Real` | sí | sí | The paragraph spacing value. |
| `thickness` | `Real` | sí | sí | The thickness of the SDF effect. |
| `coreColor` | `Array` | sí | sí | An array of 4 values, each from 0 to 1, corresponding to ARGB values of the 'core' part of the glyph. |
| `coreColour` | `Array` | sí | sí | An array of 4 values, each from 0 to 1, corresponding to ARGB values of the 'core' part of the glyph. |
| `glowStart` | `Real` | sí | sí | The distance in pixels at which the glow effect starts. |
| `glowEnd` | `Real` | sí | sí | The distance in pixels at which the glow effect ends. |
| `glowColor` | `Array` | sí | sí | An array of 4 values, each from 0 to 1, corresponding to ARGB values of the glow color. |
| `glowColour` | `Array` | sí | sí | An array of 4 values, each from 0 to 1, corresponding to ARGB values of the glow colour. |
| `outlineDist` | `Real` | sí | sí | The distance of the outline. |
| `outlineColor` | `Array` | sí | sí | An array of 4 values, each from 0 to 1, corresponding to ARGB values of the outline color. |
| `outlineColour` | `Array` | sí | sí | An array of 4 values, each from 0 to 1, corresponding to ARGB values of the outline colour. |
| `shadowSoftness` | `Real` | sí | sí | The width of the drop shadow penumbra. |
| `shadowOffsetX` | `Real` | sí | sí | The offset in pixels on the x axis of the drop shadow. |
| `shadowOffsetY` | `Real` | sí | sí | The offset in pixels on the y axis of the drop shadow. |
| `shadowColor` | `Array` | sí | sí | An array of 4 values, each from 0 to 1, holding the ARGB components of the drop shadow. |
| `shadowColour` | `Array` | sí | sí | An array of 4 values, each from 0 to 1, holding the ARGB components of the drop shadow. |
| `effectsEnabled` | `Bool` | sí | sí | Whether SDF Effects are enabled on this track. |
| `glowEnabled` | `Bool` | sí | sí | Whether the glow effect is enabled. |
| `outlineEnabled` | `Bool` | sí | sí | Whether the outline effect is enabled. |
| `dropShadowEnabled` | `Bool` | sí | sí | Whether the drop shadow effect is enabled. |

### `AnimCurve`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `name` | `String` | sí | sí |  |
| `channels` | `Array` | sí | sí |  |

### `AnimCurveChannel`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `name` | `String` | sí | sí |  |
| `type` | `Constant.AnimCurveInterpolationType` | sí | sí |  |
| `iterations` | `Real` | sí | sí |  |
| `points` | `Real` | sí | sí |  |

### `AnimCurvePoint`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `posx` | `Real` | sí | sí | The x position of the point |
| `value` | `Real` | sí | sí | The value at the x position |

### `AudioBus`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `bypass` | `Bool` | sí | sí | Whether to bypass all effects and gain scaling of the bus. |
| `gain` | `Real` | sí | sí | The output gain of the bus. |
| `effects` | `Array.Struct.AudioEffect` | sí | sí | The chain of audio effects on the bus. |

### `AudioEffect`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `attack` | `Real` | sí | sí | The response time to apply the effect. |
| `bypass` | `Bool` | sí | sí | Whether to bypass the effect. |
| `cutoff` | `Real` | sí | sí | The cutoff frequency of the filter. |
| `damp` | `Real` | sí | sí | The amount of higher frequency damping. |
| `eq1` | `Struct.AudioEffect` | sí | no | A peak EQ filter. |
| `eq2` | `Struct.AudioEffect` | sí | no | A peak EQ filter. |
| `eq3` | `Struct.AudioEffect` | sí | no | A peak EQ filter. |
| `eq4` | `Struct.AudioEffect` | sí | no | A peak EQ filter. |
| `factor` | `Real` | sí | sí | The factor by which the signal is downsampled. |
| `feedback` | `Real` | sí | sí | The proportion of the signal which is fed back into the delay line. |
| `freq` | `Real` | sí | sí | The center frequency of the filter. |
| `gain` | `Real` | sí | sí | The gain applied to the input signal. |
| `hicut` | `Struct.AudioEffect` | sí | no | A low-pass filter. |
| `hishelf` | `Struct.AudioEffect` | sí | no | A high-shelf filter. |
| `ingain` | `Real` | sí | sí | The input gain scalar. |
| `intensity` | `Real` | sí | sí | The propertion of the signal which is affected by the LFO. |
| `locut` | `Struct.AudioEffect` | sí | no | A high-pass filter. |
| `loshelf` | `Struct.AudioEffect` | sí | no | A low-shelf filter. |
| `mix` | `Real` | sí | sí | The proportion of the affected signal to output. |
| `offset` | `Real` | sí | sí | The proportion of the LFO period that the LFOs should be desynced by. |
| `outgain` | `Real` | sí | sí | The output gain scalar. |
| `q` | `Real` | sí | sí | The quality factor of the filter. |
| `rate` | `Real` | sí | sí | The frequency of the modulating LFO. |
| `ratio` | `Real` | sí | sí | The compression ratio. |
| `release` | `Real` | sí | sí | The response time to stop applying the effect. |
| `resolution` | `Real` | sí | sí | The bit depth at which the signal is resampled. |
| `shape` | `Enum.AudioLFOType` | sí | sí | The waveshape of the LFO. |
| `size` | `Real` | sí | sí | The size of the space. |
| `threshold` | `Real` | sí | sí | The gain threshold over which the effect is applied. |
| `time` | `Real` | sí | sí | The duration of the delay. |
| `type` | `Enum.AudioEffectType` | sí | no | The type of the effect. |

### `AudioTrack`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `soundIndex` | `Asset.GMSound` | sí | sí | READ-ONLY The ID of the sound instance that's playing on this track's emitter. |
| `emitterIndex` | `Id.EmitterIndex` | sí | sí | READ-ONLY The index of the audio emitter used by this track. |
| `playbackMode` | `Real` | sí | sí |  |

### `BoolTrack`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `value` | `Bool` | sí | sí | The value of the boolean |

### `ColorTrack`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `color` | `Constant.Color` | sí | sí | The color |

### `ColourTrack`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `colour` | `Constant.Color` | sí | sí | The colour |

### `Exception`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `message` | `String` | sí | sí | Short message for this exception. |
| `longMessage` | `String` | sí | sí | Long message for this exception. |
| `script` | `String` | sí | sí | Describes the script where this exception came from. |
| `stacktrace` | `Array.String` | sí | sí | The stack frame that the exception was generated from. |

### `FontEffectParams`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `thickness` | `Real` | sí | sí | Adds or removes thickness from the font. Minimum: -32, Maximum: 32. |
| `coreColour` | `Real` | sí | sí | The colour of the core part of the font (excluding any outlines, glows, etc.). |
| `coreAlpha` | `Real` | sí | sí | The alpha of the core part of the font. |
| `glowEnable` | `Bool` | sí | sí | Whether to enable or disable the Glow effect. Disabled by default. |
| `glowColour` | `Real` | sí | sí | The colour of the glow. |
| `glowAlpha` | `Real` | sí | sí | The alpha of the glow. |
| `outlineEnable` | `Bool` | sí | sí | Whether to enable or disable the Outline effect. Disabled by default. |
| `outlineDistance` | `Real` | sí | sí | The thickness of the outline from the edge of each glyph. Minimum: 0, Maximum: 64. |
| `outlineColour` | `Real` | sí | sí | The colour of the outline. |
| `outlineAlpha` | `Real` | sí | sí | The alpha of the outline. |
| `dropShadowEnable` | `Bool` | sí | sí | Enable or disable the Drop Shadow effect. Disabled by default. |
| `dropShadowSoftness` | `Real` | sí | sí | Softness or blur level of the shadow. Minimum: 0, Maximum: 64. |
| `dropShadowOffsetX` | `Real` | sí | sí | How much the shadow is moved on the X axis, 0 is the same as the text. E.g. a value of 4 moves it right by 4 pixels. |
| `dropShadowOffsetY` | `Real` | sí | sí | How much the shadow is moved on the Y axis, 0 is the same as the text. E.g. a value of 4 moves it down by 4 pixels. |
| `dropShadowColour` | `Real` | sí | sí | The colour of the shadow. |
| `dropShadowAlpha` | `Real` | sí | sí | The alpha of the shadow. |

### `FontInfo`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `ascenderOffset` | `Real` | sí | no | The maximum offset from the baseline to the top of the font (in pixels) |
| `ascender` | `Real` | sí | no | The height of the font's ascender (in pixels) |
| `sdfSpread` | `Real` | sí | no | The SDF spread value set for this font |
| `sdfEnabled` | `Bool` | sí | no | Whether SDF is enabled or disabled for this font |
| `freetype` | `Bool` | sí | no |  |
| `size` | `Real` | sí | no | The approximate size of the font (in pixels) |
| `spriteIndex` | `Asset.GMSprite` | sí | no | The sprite index for the font if it was created from a sprite, otherwise an invalid sprite handle (-1) |
| `texture` | `Asset.GMTexturePage` | sí | no | -1 if the font was created from a sprite, otherwise the texture ID of the font |
| `name` | `String` | sí | no | The name of the font |
| `bold` | `Bool` | sí | no | true if the font is bold, otherwise false |
| `italic` | `Bool` | sí | no | true if the font is italic, otherwise false |
| `effectsEnabled` | `Bool` | sí | no | Whether effects are enabled for this font |
| `effectParams` | `Struct` | sí | no | The effects struct for this font, which can be changed with font_enable_effects |
| `glyphs` | `Struct` | sí | no | A struct containing information for each glyph in the font |

### `FontInfoGlyph`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `char` | `Real` | sí | no | If the font was created from a sprite, this will be the image index of the glyph from that sprite, otherwise it will be its Unicode character number. Note: All  |
| `x` | `Real` | sí | no | The X position of the glyph on the texture page (in texels) |
| `y` | `Real` | sí | no | The Y position of the glyph on the texture page (in texels) |
| `w` | `Real` | sí | no | The width of the glyph on the texture page (in texels) |
| `h` | `Real` | sí | no | The height of the glyph on the texture page (in texels) |
| `shift` | `Real` | sí | no | The number of pixels to shift right when advancing to the next character (can be negative for shifting left) |
| `offset` | `Real` | sí | no | The number of pixels to horizontally offset the rendering of this glyph without affecting the shift position (can be positive or negative) |
| `kerning` | `Array` | sí | no | An array of integers containing kerning information in pairs (or groups of 2). The first integer in a pair is the Unicode value for a character, and the second  |

### `GCStats`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `objects_touched` | `Real` | sí | sí | This is the number of active objects the garbage collector found in the previous frame. This will vary depending on which generation was collected. |
| `objects_collected` | `Real` | sí | sí | The number of objects which the garbage collector determined weren't active in the previous frame, and which could therefore be deleted. |
| `traversal_time` | `Real` | sí | sí | This is the time in microseconds (on the main thread) which the garbage collector took to figure out which objects were active. |
| `collection_time` | `Real` | sí | sí | This is the time in microseconds (on a separate thread) which the garbage collector took to clean up the objects deemed inactive. |
| `gc_frame` | `Real` | sí | sí | This is a counter which is incremented every time a garbage collection pass occurs. If garbage collection is disabled this will not increase. |
| `generation_collected` | `Real` | sí | sí | This is the index of the generation that was collected last. 0 is the youngest generation and 3 is currently the oldest. |
| `num_generations` | `Real` | sí | sí | This is the total number of garbage collection generations. |
| `num_objects_in_generation` | `Array` | sí | sí | This is an array (of size num_generations) containing the number of objects in each generation. |

### `GraphicTrack`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `spriteIndex` | `Asset.GMSprite` | sí | sí | The sprite asset used by the graphic track |

### `InstanceTrack`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `objectIndex` | `Asset.GMObject` | sí | sí | The object index of the instance |

### `KeyChannel`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `channel` | `Real` | sí | sí | The key's channel |

### `Keyframe`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `frame` | `Real` | sí | sí | The position (in frames) along the timeline for the keyframe. Default value is 0. |
| `length` | `Real` | sí | sí | The length of the keyframe. Default value is 1, and when set to larger values then the track property that the keyframe refers to will be maintained at the init |
| `stretch` | `Bool` | sí | sí | If this property is set to true then the keyframe stretches to either the next keyframe for the track or to the end of the track if it's the last keyframe. You  |
| `disabled` | `Bool` | sí | sí | Whether this keyframe is disabled |
| `channels` | `Array` | sí | sí | This property allows access to the list of keyframe data structs for the channels of the track. When getting this property an array of keyframe data structs is  |

### `MessageEvent`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `events` | `Array` | sí | sí |  |

### `Moment`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `event` | `Real` | sí | sí |  |

### `RealTrack`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `value` | `Real` | sí | sí | The value to use |
| `curve` | `Real` | sí | sí |  |

### `Sequence`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `name` | `String` | sí | sí | This is the name of the sequence as a string and you can get or set this value as required. Note that sequences created using the function sequence_create() wil |
| `loopmode` | `Constant.SeqPlay` | sí | sí | This is the playback mode of the sequence object and can be get or set. |
| `playbackSpeed` | `Real` | sí | sí | This specifies the playback speed of the sequence, which is interpreted as either frames-per-second or frames-per-game-frame depending on the playbackSpeedType. |
| `playbackSpeedType` | `Constant.SpriteSpeed` | sí | sí | This specifies how the playbackSpeed should be interpreted and you can get or set this value. |
| `length` | `Real` | sí | sí | The length of the sequence in frames. You can get or set this value, but note that making a sequence shorter may cause issues if a sequence instance referencing |
| `volume` | `Real` | sí | sí | This is a scalar value from 0 to 1 that is used to scale the volume of all audio tracks in the sequence. You can get or set this value and it will modify the gl |
| `xorigin` | `Real` | sí | sí | This is the origin of the sequence along the X axis. |
| `yorigin` | `Real` | sí | sí | This is the origin of the sequence along the Y axis. |
| `messageEventKeyframes` | `Array` | sí | sí | This allows access to the message event keyframes for the sequence. You can get or set these message events, and when getting this property an array of keyframe |
| `momentKeyframes` | `Array` | sí | sí | This allows access to the moment event keyframes for the sequence. You can get or set these moment events, and when getting this property an array of keyframe s |
| `tracks` | `Array` | sí | sí | This allows access to the list of asset tracks on the top level of the sequence. You can get or set this property, and when getting this property an array of tr |

### `SequenceInstance`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `sequence` | `Struct.Sequence` | sí | sí | This is the ID of the sequence object struct that the sequence instance has been created from. |
| `headPosition` | `Real` | sí | sí | This is the current playhead position (in frames) for the sequence instance. |
| `headDirection` | `Constant.SequenceDirection` | sí | sí | This is the current playback direction for the sequence instance. |
| `speedScale` | `Real` | sí | sí | This property can be used to get or set the playback speed scale. |
| `volume` | `Real` | sí | sí | This is a scalar value from 0 to 1 that is used to scale the volume of all audio tracks in the sequence. You can get or set this value and it will modify the gl |
| `paused` | `Bool` | sí | sí | You can check this read-only property to see if a sequence has been paused or not, and it will be true if it has, or false otherwise. |
| `finished` | `Bool` | sí | sí | You can check this read-only property to see if a sequence has finished playing or not, returning true if it is finished playing, and false otherwise. |
| `activeTracks` | `Array[Struct.ActiveTrack]` | sí | sí | This read-only property will hold an array of "evaluation" structs containing information on the current state of each asset track in the sequence (graphics, se |
| `elementID` | `Id.SequenceElement` | sí | sí | This property holds the ID of the sequence element. |

### `SequenceTrack`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `sequence` | `Undefined` | sí | sí | The sequence used by the sequence track |

### `SpriteTrack`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `imageIndex` | `Real` | sí | sí | The image index |

### `StringTrack`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `value` | `String` | sí | sí | The string |

### `TextTrack`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `text` | `String` | sí | sí | The text shown on the text track |
| `wrap` | `Bool` | sí | sí | Whether to wrap the text |
| `alignmentV` | `Real` | sí | sí | The horizontal text alignment |
| `alignmentH` | `Real` | sí | sí | The vertical text alignment |
| `fontIndex` | `Asset.GMFont` | sí | sí | The index of the font asset |
| `effectsEnabled` | `Bool` | sí | sí | Whether SDF text effects are enabled or not |
| `glowEnabled` | `Bool` | sí | sí | Whether the glow effect is enabled |
| `outlineEnabled` | `Bool` | sí | sí | Whether the outline effect is enabled |
| `dropShadowEnabled` | `Bool` | sí | sí | Whether the drop shadow effect is enabled |

### `TileSetInfo`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `width` | `Real` | sí | no | The width of the whole tile set texture (in pixels). |
| `height` | `Real` | sí | no | The height of the whole tile set texture (in pixels). |
| `texture` | `Real` | sí | no | The texture ID. |
| `tile_width` | `Real` | sí | no | The width of a single tile (in pixels). |
| `tile_height` | `Real` | sí | no | The height of a single tile (in pixels). |
| `tile_horizontal_separator` | `Real` | sí | no | The number of pixels horizontally on each side of each tile (making the space between two tiles 2 * tile_horizontal_separator). |
| `tile_vertical_separator` | `Real` | sí | no | The number of pixels vertically on each side of each tile (making the space between two tiles 2 * tile_vertical_separator) |
| `tile_columns` | `Real` | sí | no | The number of columns on each row of the tile set. |
| `tile_count` | `Real` | sí | no | The number of tiles. |
| `frame_count` | `Real` | sí | no | The number of frames of animation per animation. |
| `frame_length_ms` | `Real` | sí | no | The number of milliseconds for frame animation. |
| `frames` | `Struct` | sí | no | A struct containing all the animation frames. Each tile number has a key in the struct, each entry is an array of the frames to use (each array should be frame_ |

### `Track`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `name` | `String` | sí | sí | When creating a "top-level" asset track, the name you give here can be any string that you require to identify the track. However, for parameter tracks, you nee |
| `type` | `Constant.SequenceTrackType` | sí | sí | This contains a Sequence Track Type Constant that describes the type of track. |
| `tracks` | `Array[Struct.Track]` | sí | sí | The list of tracks which are children of this track. When getting this property an array of Sequence Track Structs is returned, and when setting this property a |
| `visible` | `Bool` | sí | sí | This indicates whether this track is visible (the value is true) or not (the value is false). You can get or set this value and if a track not visible then none |
| `keyframes` | `Array[Struct.Keyframe]` | sí | sí | This property allows access to the list of keyframe structs for the track. When getting this property an array of keyframe structs is returned, and when setting |

### `VertexElementInfo`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `usage` | `Constant.VertexUsage` | sí | no | The usage of the vertex attribute |
| `type` | `Constant.VertexType` | sí | no | The type of the vertex attribute |
| `size` | `Real` | sí | no | The size of the vertex attribute |
| `offset` | `Real` | sí | no | The offset of the vertex attribute |

### `VertexFormatInfo`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `stride` | `Real` | sí | no | The total size in bytes of a single vertex |
| `num_elements` | `Real` | sí | no | The number of elements (vertex attributes) in a single vertex |
| `elements` | `array[Struct.VertexElementInfo]` | sí | no | An array of elements. |

### `WeakRef`

| Campo | Tipo | Lectura | Escritura | Descripción |
|---|---|---|---|---|
| `ref` | `ArgumentIdentity` | sí | sí | The strong reference to the struct in question, or undefined if it has been garbage collected. |
