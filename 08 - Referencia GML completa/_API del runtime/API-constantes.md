# Referencia de la API de GML — constantes y enumeraciones

> Runtime **2026.0.0.23**. 886 constantes y 13 enumeraciones.

## Constantes por clase


### All

| Constante | Tipo | Descripción |
|---|---|---|
| `all` | `Id.Instance` | The all keyword |

### AnimCurveInterpolationType

| Constante | Tipo | Descripción |
|---|---|---|
| `animcurvetype_bezier` | `Real` | Used for Bezier interpolation between points. |
| `animcurvetype_catmullrom` | `Real` | Used for smooth interpolation between points using Catmull-Rom interpolation. |
| `animcurvetype_linear` | `Real` | Used for linear interpolation between points. |

### AssetType

| Constante | Tipo | Descripción |
|---|---|---|
| `asset_animationcurve` | `Real` | The given name refers to an Animation Curve. |
| `asset_font` | `Real` | The given name refers to a font. |
| `asset_object` | `Real` | The given name refers to an object. |
| `asset_particlesystem` | `Real` | The given name refers to a Particle System. |
| `asset_path` | `Real` | The given name refers to a path. |
| `asset_room` | `Real` | The given name refers to a room. |
| `asset_script` | `Real` | The given name refers to a script. |
| `asset_sequence` | `Real` | The given name refers to a Sequence. |
| `asset_shader` | `Real` | The given name refers to a shader. |
| `asset_sound` | `Real` | The given name refers to a sound. |
| `asset_sprite` | `Real` | The given name refers to a sprite. |
| `asset_tiles` | `Real` | The given name refers to a tile set. |
| `asset_timeline` | `Real` | The given name refers to a time line. |
| `asset_unknown` | `Real` | The given name refers to an asset that either does not exist, or is not one of the above listed. |

### AsyncEventType

| Constante | Tipo | Descripción |
|---|---|---|
| `ev_async_audio_playback` | `Real` | Audio Playback event |
| `ev_async_audio_playback_ended` | `Real` | Audio Playback Ended event |
| `ev_async_audio_recording` | `Real` | Audio Recording event |
| `ev_async_dialog` | `Real` | Dialog event |
| `ev_async_push_notification` | `Real` | Push Notification event |
| `ev_async_save_load` | `Real` | Save/Load Event |
| `ev_async_social` | `Real` | Social event |
| `ev_async_system_event` | `Real` | System event |
| `ev_async_web` | `Real` | Web event |
| `ev_async_web_cloud` | `Real` | Cloud event |
| `ev_async_web_iap` | `Real` | In-App Purchase event |
| `ev_async_web_image_load` | `Real` | Image Loaded event |
| `ev_async_web_networking` | `Real` | Networking event |
| `ev_async_web_steam` | `Real` | Steam event |

### AudioChannelType

| Constante | Tipo | Descripción |
|---|---|---|
| `audio_3d` | `Real` | 3D (5.1) audio. |
| `audio_mono` | `Real` | Mono (single channel) audio. |
| `audio_stereo` | `Real` | Stereo (dual channel) audio. |

### AudioFalloff

| Constante | Tipo | Descripción |
|---|---|---|
| `audio_falloff_exponent_distance` | `Real` | gain = (listener_distance / reference_distance) ^ (-falloff_factor) |
| `audio_falloff_exponent_distance_clamped` | `Real` | distance = clamp(listener_distance, reference_distance, maximum_distance) gain = (distance / reference_distance) ^ (-falloff_factor) |
| `audio_falloff_exponent_distance_scaled` | `Real` | distance = clamp(listener_distance, reference_distance, maximum_distance) gain = ((distance / reference_distance) ^ (-falloff_factor)) * (((maximum_distance - distance) / (maximum_ |
| `audio_falloff_inverse_distance` | `Real` | gain = reference_distance / (reference_distance + falloff_factor * (listener_distance - reference_distance)) |
| `audio_falloff_inverse_distance_clamped` | `Real` | distance = clamp(listener_distance, reference_distance, maximum_distance) gain = reference_distance / (reference_distance + falloff_factor * (distance - reference_distance)) |
| `audio_falloff_inverse_distance_scaled` | `Real` | distance = clamp(listener_distance, reference_distance, maximum_distance) gain = (reference_distance / (reference_distance + falloff_factor * (distance - reference_distance))) * (( |
| `audio_falloff_linear_distance` | `Real` | distance = min(distance, maximum_distance) gain = (1 - falloff_factor * (distance - reference_distance) / (maximum_distance - reference_distance)) |
| `audio_falloff_linear_distance_clamped` | `Real` | distance = clamp(listener_distance, reference_distance, maximum_distance) gain = (1 - falloff_factor * (distance - reference_distance) / (maximum_distance - reference_distance)) |
| `audio_falloff_none` | `Real` | gain = 1 |

### BBoxMode

| Constante | Tipo | Descripción |
|---|---|---|
| `bboxmode_automatic` | `Real` | Automatic - The bounding box will be calculated automatically, based on the tolerance setting for the sprite |
| `bboxmode_fullimage` | `Real` | Full Image - The bounding box will be set to use the full width and height of the sprite, regardless of the tolerance and "empty" pixels |
| `bboxmode_manual` | `Real` | Manual - The bounding box has been set manually to user-defined values (either in the sprite editor, or using the function sprite_set_bbox()) |

### BlendMode

| Constante | Tipo | Descripción |
|---|---|---|
| `bm_add` | `Real` | Additive blending. Luminosity values of light areas are added. |
| `bm_max` | `Real` | Max blending. Similar to additive blending. |
| `bm_min` | `Real` | Min blending (Takes the minimum value for each colour component). |
| `bm_normal` | `Real` | Normal blending (the default blend mode). |
| `bm_reverse_subtract` | `Real` | Subtractive blending where the destination colour is subtracted from the source colour. |
| `bm_subtract` | `Real` | Subtractive blending where the source colour is subtracted from the destination colour. |

### BlendModeEquation

| Constante | Tipo | Descripción |
|---|---|---|
| `bm_eq_add` | `Real` | Additive blending. Luminosity values of light areas are added. |
| `bm_eq_max` | `Real` | Max blending (Takes the maximum value for each colour component). |
| `bm_eq_min` | `Real` | Min blending (Takes the minimum value for each colour component). |
| `bm_eq_reverse_subtract` | `Real` | Subtractive blending where the destination colour is subtracted from the source colour. |
| `bm_eq_subtract` | `Real` | Subtractive blending where the source colour is subtracted from the destination colour. |

### BlendModeFactor

| Constante | Tipo | Descripción |
|---|---|---|
| `bm_dest_alpha` | `Real` | (Ad, Ad, Ad, Ad) |
| `bm_dest_color` | `Real` | (Rd, Gd, Bd, Ad) |
| `bm_dest_colour` | `Real` | (Rd, Gd, Bd, Ad) |
| `bm_inv_dest_alpha` | `Real` | (1-Ad, 1-Ad, 1-Ad, 1-Ad) |
| `bm_inv_dest_color` | `Real` | (1-Rd, 1-Gd, 1-Bd, 1-Ad) |
| `bm_inv_dest_colour` | `Real` | (1-Rd, 1-Gd, 1-Bd, 1-Ad) |
| `bm_inv_src_alpha` | `Real` | (1-As, 1-As, 1-As, 1-As) |
| `bm_inv_src_color` | `Real` | (1-Rs, 1-Gs, 1-Bs, 1-As) |
| `bm_inv_src_colour` | `Real` | (1-Rs, 1-Gs, 1-Bs, 1-As) |
| `bm_one` | `Real` | (1, 1, 1, 1) |
| `bm_src_alpha` | `Real` | (As, As, As, As) |
| `bm_src_alpha_sat` | `Real` | (f, f, f, 1) where f = min(As, 1-Ad) |
| `bm_src_color` | `Real` | (Rs, Gs, Bs, As) |
| `bm_src_colour` | `Real` | (Rs, Gs, Bs, As) |
| `bm_zero` | `Real` | (0, 0, 0, 0) |

### Browser

| Constante | Tipo | Descripción |
|---|---|---|
| `browser_edge` | `Real` | Edge browser |

### BrowserType

| Constante | Tipo | Descripción |
|---|---|---|
| `browser_chrome` | `Real` | Google Chrome |
| `browser_firefox` | `Real` | Mozilla Firefox |
| `browser_ie` | `Real` | Internet Explorer |
| `browser_ie_mobile` | `Real` | Internet Explorer on a mobile device |
| `browser_not_a_browser` | `Real` | Game is not being played in a browser |
| `browser_opera` | `Real` | Opera |
| `browser_safari` | `Real` | Safari |
| `browser_safari_mobile` | `Real` | Safari on a mobile device |
| `browser_tizen` | `Real` | Tizen mobile device browser |
| `browser_unknown` | `Real` | Unknown browser |
| `browser_windows_store` | `Real` | Windows App |

### BufferDataType

| Constante | Tipo | Descripción |
|---|---|---|
| `buffer_bool` | `Real` | A boolean value. Can only be either 1 or 0 (true or false) |
| `buffer_f16` | `Real` | A 16bit float. This can be a positive or negative value within the range of +/- 65504. (Not currently supported!) |
| `buffer_f32` | `Real` | A 32bit float. This can be a positive or negative value within the range of +/-16777216. |
| `buffer_f64` | `Real` | A 64bit float. |
| `buffer_s16` | `Real` | A signed, 16bit integer. This can be a positive or negative value from -32,768 to 32,767 (0 is classed as positive). |
| `buffer_s32` | `Real` | A signed, 32bit integer. This can be a positive or negative value from -2,147,483,648 to 2,147,483,647 (0 is classed as positive). |
| `buffer_s8` | `Real` | A signed, 8bit integer. This can be a positive or negative value from -128 to 127 (0 is classed as positive). |
| `buffer_string` | `Real` | A string of any size. |
| `buffer_text` | `Real` | A string of any size, without the final null terminating character. |
| `buffer_u16` | `Real` | An unsigned, 16bit integer. This is a positive value from 0 - 65,535. |
| `buffer_u32` | `Real` | An unsigned, 32bit integer. This is a positive value from 0 to 4,294,967,295. |
| `buffer_u64` | `Real` | An unsigned 64bit integer. |
| `buffer_u8` | `Real` | An unsigned, 8bit integer. This is a positive value from 0 to 255. |

### BufferErrorType

| Constante | Tipo | Descripción |
|---|---|---|
| `buffer_error_general` | `Real` | General buffer error. |
| `buffer_error_invalid_type` | `Real` | Attempting to write an invalid type to a buffer. |
| `buffer_error_out_of_space` | `Real` | Attempting to write to a buffer that doesn't have enough space for the size of the type being written. |

### BufferType

| Constante | Tipo | Descripción |
|---|---|---|
| `buffer_fast` | `Real` | Special "stripped" buffer that is extremely fast to read/write to. Can only be used with buffer_u8 data types, and must be 1 byte aligned. |
| `buffer_fixed` | `Real` | A buffer of fixed size. |
| `buffer_grow` | `Real` | A buffer that will "grow" dynamically as data is added |
| `buffer_vbuffer` | `Real` | This type of buffer is to be used as a vertex buffer only. |
| `buffer_wrap` | `Real` | A buffer where the data will "wrap". When the data being added reaches the limit of the buffer size, the overwrite will be placed back at the start of the buffer, and further writi |

### CollisionMask

| Constante | Tipo | Descripción |
|---|---|---|
| `bboxkind_diamond` | `Real` | A diamond collision mask shape |
| `bboxkind_ellipse` | `Real` | An elliptical collision mask shape |
| `bboxkind_precise` | `Real` | A precise collision mask, where the mask will conform to the non-transparent pixels of the sprite, based on the tolerance value given |
| `bboxkind_rectangular` | `Real` | A rectangular (non-rotating) rectangle collision mask shape |
| `bboxkind_spine` | `Real` | Collision mesh from Spine sprite |

### Color

| Constante | Tipo | Descripción |
|---|---|---|
| `c_aqua` | `Real` | #00ffff |
| `c_black` | `Real` | #000000 |
| `c_blue` | `Real` | #0000ff |
| `c_dkgray` | `Real` | #404040 |
| `c_dkgrey` | `Real` | #404040 |
| `c_fuchsia` | `Real` | #ff00ff |
| `c_gray` | `Real` | #808080 |
| `c_green` | `Real` | #008000 |
| `c_grey` | `Real` | #808080 |
| `c_lime` | `Real` | #00ff00 |
| `c_ltgray` | `Real` | #c0c0c0 |
| `c_ltgrey` | `Real` | #c0c0c0 |
| `c_maroon` | `Real` | #800000 |
| `c_navy` | `Real` | #000080 |
| `c_olive` | `Real` | #808000 |
| `c_orange` | `Real` | #ffa040 |
| `c_purple` | `Real` | #800080 |
| `c_red` | `Real` | #ff0000 |
| `c_silver` | `Real` | #c0c0c0 |
| `c_teal` | `Real` | #008080 |
| `c_white` | `Real` | #ffffff |
| `c_yellow` | `Real` | #ffff00 |

### CullMode

| Constante | Tipo | Descripción |
|---|---|---|
| `cull_clockwise` | `Real` | All clockwise triangles will be culled |
| `cull_counterclockwise` | `Real` | All counter-clockwise triangles will be culled |
| `cull_noculling` | `Real` | No culling will be done |

### Cursor

| Constante | Tipo | Descripción |
|---|---|---|
| `cr_appstart` | `Real` |  |
| `cr_arrow` | `Real` |  |
| `cr_beam` | `Real` |  |
| `cr_cross` | `Real` |  |
| `cr_default` | `Real` |  |
| `cr_drag` | `Real` |  |
| `cr_handpoint` | `Real` |  |
| `cr_hourglass` | `Real` |  |
| `cr_none` | `Real` |  |
| `cr_size_all` | `Real` |  |
| `cr_size_nesw` | `Real` |  |
| `cr_size_ns` | `Real` |  |
| `cr_size_nwse` | `Real` |  |
| `cr_size_we` | `Real` |  |
| `cr_uparrow` | `Real` |  |

### DebugInputFilter

| Constante | Tipo | Descripción |
|---|---|---|
| `debug_input_filter_keyboard` | `Real` | Include keyboard input |
| `debug_input_filter_mouse` | `Real` | Include mouse input |
| `debug_input_filter_touch` | `Real` | Include touch input |

### DeviceType

| Constante | Tipo | Descripción |
|---|---|---|
| `device_emulator` | `Real` | The device is actually an emulator (Windows Phone or Android) |
| `device_ios_ipad` | `Real` | iPad |
| `device_ios_ipad_retina` | `Real` | Newer iPad with Retina display size of 2048 x 1536 |
| `device_ios_iphone` | `Real` | Older iPhone/iPod Touch (480 x 320 screen) or Android phone |
| `device_ios_iphone5` | `Real` | iPhone5 with display size 640 x 1136) |
| `device_ios_iphone6` | `Real` | iPhone6 with display size 1334 x 750 |
| `device_ios_iphone6plus` | `Real` | Larger iPhone 6 with display 1920 x 1080 |
| `device_ios_iphone_retina` | `Real` | Newer iPhone/iPod Touch with Retina display of 960 x 640 |
| `device_ios_unknown` | `Real` | Unknown or not iOS |
| `device_tablet` | `Real` | Android tablet |

### DsType

| Constante | Tipo | Descripción |
|---|---|---|
| `ds_type_grid` | `Real` | A grid data structure |
| `ds_type_list` | `Real` | A list data structure |
| `ds_type_map` | `Real` | A map data structure |
| `ds_type_priority` | `Real` | A priority data structure |
| `ds_type_queue` | `Real` | A queue data structure |
| `ds_type_stack` | `Real` | A stack data structure |

### EffectType

| Constante | Tipo | Descripción |
|---|---|---|
| `ef_cloud` | `Real` | Random cloud particles of varying sizes |
| `ef_ellipse` | `Real` | An effect that creates expanding ellipses |
| `ef_explosion` | `Real` | An effect that creates expanding fading explosions |
| `ef_firework` | `Real` | An effect that creates multiple small particles to generate a firework explosion |
| `ef_flare` | `Real` | An effect that generates a brilliant point that flares up and fades out |
| `ef_rain` | `Real` | An effect that generates rain particles coming down from the top of the screen |
| `ef_ring` | `Real` | An effect that generates expanding and fading circles |
| `ef_smoke` | `Real` | An effect that generates little puffs of smoke |
| `ef_smokeup` | `Real` | An effect that creates a smoke plume that rises up the screen |
| `ef_snow` | `Real` | An effect that generates multiple snow particles falling down the screen |
| `ef_spark` | `Real` | An effect that generates a small spark |
| `ef_star` | `Real` | An effect that generates star particles |

### EventNumber

| Constante | Tipo | Descripción |
|---|---|---|
| `ev_animation_end` | `Real` | If the object's sprite has reached the end of its animation |
| `ev_animation_event` | `Real` | Animation event that runs for skeletal animations as assigned in the skeletal animation tool |
| `ev_animation_update` | `Real` | Animation event that runs every step for objects that use skeletal animations |
| `ev_audio_playback` ⚠️obsoleta | `Real` |  |
| `ev_audio_playback_ended` ⚠️obsoleta | `Real` |  |
| `ev_audio_recording` ⚠️obsoleta | `Real` |  |
| `ev_boundary` | `Real` | Whether the instance is intersecting the boundary |
| `ev_boundary_view0` | `Real` | Whether the instance is interesecting with the boundary of the given view (0 to 7) |
| `ev_boundary_view1` | `Real` |  |
| `ev_boundary_view2` | `Real` |  |
| `ev_boundary_view3` | `Real` |  |
| `ev_boundary_view4` | `Real` |  |
| `ev_boundary_view5` | `Real` |  |
| `ev_boundary_view6` | `Real` |  |
| `ev_boundary_view7` | `Real` |  |
| `ev_broadcast_message` | `Real` | Broadcast Message event used for sprites and sequences |
| `ev_dialog_async` ⚠️obsoleta | `Real` |  |
| `ev_draw_begin` | `Real` | The draw begin event. |
| `ev_draw_end` | `Real` | The draw end event. |
| `ev_draw_normal` | `Real` | The normal draw event. |
| `ev_draw_post` | `Real` | The post draw event. |
| `ev_draw_pre` | `Real` | The pre draw event. |
| `ev_end_of_path` | `Real` | If the object has reached the end of the path it is following |
| `ev_game_end` | `Real` | Only triggered at the end of the game |
| `ev_game_start` | `Real` | Only triggered at the start of the game |
| `ev_gesture_double_tap` | `Real` | Two quick touches/clicks and releases have been detected for an instance |
| `ev_gesture_drag_end` | `Real` | The release of the touch/click from a drag has been detected for an instance |
| `ev_gesture_drag_start` | `Real` | The beginning of a drag gesture has been detected for an instance |
| `ev_gesture_dragging` | `Real` | A touch/click has been held and moved for an instance |
| `ev_gesture_flick` | `Real` | The release of a touch/click from a drag had enough movement for a flick event to be detected for the instance |
| `ev_gesture_pinch_end` | `Real` | The release of one (or both) touches for a pinch has been detected for an instance |
| `ev_gesture_pinch_in` | `Real` | The movement between two touches for an instance has been detected as inwards |
| `ev_gesture_pinch_out` | `Real` | The movement between two touches for an instance has been detected as outwards |
| `ev_gesture_pinch_start` | `Real` | Two touches and a straight movement have been detected for an instance |
| `ev_gesture_rotate_end` | `Real` | The release of one (or both) touches for a rotation has been detected for an instance |
| `ev_gesture_rotate_start` | `Real` | The movement between two touches for an instance has been detected as a rotation |
| `ev_gesture_rotating` | `Real` | The movement between two touches for an instance has been detected as rotating |
| `ev_gesture_tap` | `Real` | A single click/touch and release has been detected for an instance |
| `ev_global_gesture_double_tap` | `Real` | Two quick touches/clicks and releases have been detected anywhere in the room |
| `ev_global_gesture_drag_end` | `Real` | The release of the touch/click from a drag has been detected anywhere in the room |
| `ev_global_gesture_drag_start` | `Real` | The beginning of a drag gesture has been detected anywhere in the room |
| `ev_global_gesture_dragging` | `Real` | A touch/click has been held and moved anywhere in the room |
| `ev_global_gesture_flick` | `Real` | The release of a touch/click from a drag had enough movement for a flick event to be detected anywhere in the room |
| `ev_global_gesture_pinch_end` | `Real` | The release of one (or both) touches for a pinch has been detected anywhere in the room |
| `ev_global_gesture_pinch_in` | `Real` | The movement between two touches anywhere in the room has been detected as inwards |
| `ev_global_gesture_pinch_out` | `Real` | The movement between two touches anywhere in the room has been detected as outwards |
| `ev_global_gesture_pinch_start` | `Real` | Two touches and a straight movement have been detected anywhere in the room |
| `ev_global_gesture_rotate_end` | `Real` | The release of one (or both) touches for a rotation has been detected anywhere in the room |
| `ev_global_gesture_rotate_start` | `Real` | The movement between two touches anywhere in the room has been detected as a rotation |
| `ev_global_gesture_rotating` | `Real` | The movement between two touches anywhere in the room has been detected as rotating |
| `ev_global_gesture_tap` | `Real` | A single click/touch and release has been detected anywhere in the room |
| `ev_global_left_button` | `Real` | Left button held down anywhere |
| `ev_global_left_press` | `Real` | Left button just pressed anywhere |
| `ev_global_left_release` | `Real` | Left button just released anywhere |
| `ev_global_middle_button` | `Real` | Middle button (or clickable wheel) held down anywhere |
| `ev_global_middle_press` | `Real` | Middle button (or clickable wheel) just pressed anywhere |
| `ev_global_middle_release` | `Real` | Middle button just released anywhere |
| `ev_global_right_button` | `Real` | Right button held down anywhere |
| `ev_global_right_press` | `Real` | Right button just pressed anywhere |
| `ev_global_right_release` | `Real` | Right button just released anywhere |
| `ev_gui` | `Real` | The draw gui event. |
| `ev_gui_begin` | `Real` | The draw gui begin event. |
| `ev_gui_end` | `Real` | The draw gui end event. |
| `ev_joystick1_button1` ⚠️obsoleta | `Real` |  |
| `ev_joystick1_button2` ⚠️obsoleta | `Real` |  |
| `ev_joystick1_button3` ⚠️obsoleta | `Real` |  |
| `ev_joystick1_button4` ⚠️obsoleta | `Real` |  |
| `ev_joystick1_button5` ⚠️obsoleta | `Real` |  |
| `ev_joystick1_button6` ⚠️obsoleta | `Real` |  |
| `ev_joystick1_button7` ⚠️obsoleta | `Real` |  |
| `ev_joystick1_button8` ⚠️obsoleta | `Real` |  |
| `ev_joystick1_down` ⚠️obsoleta | `Real` |  |
| `ev_joystick1_left` ⚠️obsoleta | `Real` |  |
| `ev_joystick1_right` ⚠️obsoleta | `Real` |  |
| `ev_joystick1_up` ⚠️obsoleta | `Real` |  |
| `ev_joystick2_button1` ⚠️obsoleta | `Real` |  |
| `ev_joystick2_button2` ⚠️obsoleta | `Real` |  |
| `ev_joystick2_button3` ⚠️obsoleta | `Real` |  |
| `ev_joystick2_button4` ⚠️obsoleta | `Real` |  |
| `ev_joystick2_button5` ⚠️obsoleta | `Real` |  |
| `ev_joystick2_button6` ⚠️obsoleta | `Real` |  |
| `ev_joystick2_button7` ⚠️obsoleta | `Real` |  |
| `ev_joystick2_button8` ⚠️obsoleta | `Real` |  |
| `ev_joystick2_down` ⚠️obsoleta | `Real` |  |
| `ev_joystick2_left` ⚠️obsoleta | `Real` |  |
| `ev_joystick2_right` ⚠️obsoleta | `Real` |  |
| `ev_joystick2_up` ⚠️obsoleta | `Real` |  |
| `ev_left_button` | `Real` | Left button held down on object |
| `ev_left_press` | `Real` | Left button just pressed on object |
| `ev_left_release` | `Real` | Left button just released on object |
| `ev_middle_button` | `Real` | Middle button (or clickable wheel) held down on object |
| `ev_middle_press` | `Real` | Middle button (or clickable wheel) just pressed on object |
| `ev_middle_release` | `Real` | Middle button just released on object |
| `ev_mouse_enter` | `Real` | Mouse just entered object's bounding box |
| `ev_mouse_leave` | `Real` | Mouse just left object's bounding box |
| `ev_mouse_wheel_down` | `Real` | Mouse wheel scrolled downwards |
| `ev_mouse_wheel_up` | `Real` | Mouse wheel scrolled upwards |
| `ev_no_button` | `Real` | No buttons held down |
| `ev_no_more_health` ⚠️obsoleta | `Real` |  |
| `ev_no_more_lives` ⚠️obsoleta | `Real` |  |
| `ev_outside` | `Real` | Whether the instance is outside of the room |
| `ev_outside_view0` | `Real` | Whether the instance is outside the given view (0 to 7) |
| `ev_outside_view1` | `Real` |  |
| `ev_outside_view2` | `Real` |  |
| `ev_outside_view3` | `Real` |  |
| `ev_outside_view4` | `Real` |  |
| `ev_outside_view5` | `Real` |  |
| `ev_outside_view6` | `Real` |  |
| `ev_outside_view7` | `Real` |  |
| `ev_push_notification` ⚠️obsoleta | `Real` |  |
| `ev_right_button` | `Real` | Right button held down on object |
| `ev_right_press` | `Real` | Right button just pressed on object |
| `ev_right_release` | `Real` | Right button just released on object |
| `ev_room_end` | `Real` | Only triggered at the end of a room |
| `ev_room_start` | `Real` | Only triggered at the start of a room |
| `ev_social` ⚠️obsoleta | `Real` |  |
| `ev_step_begin` | `Real` | Begin Step |
| `ev_step_end` | `Real` | End Step |
| `ev_step_normal` | `Real` | Step |
| `ev_system_event` ⚠️obsoleta | `Real` |  |
| `ev_user0` | `Real` | One of the 16 available user events. |
| `ev_user1` | `Real` |  |
| `ev_user10` | `Real` |  |
| `ev_user11` | `Real` |  |
| `ev_user12` | `Real` |  |
| `ev_user13` | `Real` |  |
| `ev_user14` | `Real` |  |
| `ev_user15` | `Real` |  |
| `ev_user2` | `Real` |  |
| `ev_user3` | `Real` |  |
| `ev_user4` | `Real` |  |
| `ev_user5` | `Real` |  |
| `ev_user6` | `Real` |  |
| `ev_user7` | `Real` |  |
| `ev_user8` | `Real` |  |
| `ev_user9` | `Real` |  |
| `ev_web_async` ⚠️obsoleta | `Real` |  |
| `ev_web_cloud` ⚠️obsoleta | `Real` |  |
| `ev_web_iap` ⚠️obsoleta | `Real` |  |
| `ev_web_image_load` ⚠️obsoleta | `Real` |  |
| `ev_web_networking` ⚠️obsoleta | `Real` |  |
| `ev_web_sound_load` ⚠️obsoleta | `Real` |  |
| `ev_web_steam` ⚠️obsoleta | `Real` |  |

### EventType

| Constante | Tipo | Descripción |
|---|---|---|
| `ev_alarm` | `Real` | Alarm event |
| `ev_cleanup` | `Real` | Clean Up Event |
| `ev_collision` | `Real` | Collision with an object |
| `ev_create` | `Real` | Create event |
| `ev_destroy` | `Real` | Destroy event |
| `ev_draw` | `Real` | Draw event. NOTE: This event cannot be forced outside of a draw event and the constants and the constants are only for identifying the event when performed in these cases. |
| `ev_gesture` | `Real` | A gesture event (Tap, Drag, Flick, Pinch or Rotate) |
| `ev_keyboard` | `Real` | Keyboard/Keyboard Pressed/Keyboard Released |
| `ev_keypress` | `Real` |  |
| `ev_keyrelease` | `Real` |  |
| `ev_mouse` | `Real` | Mouse event |
| `ev_other` | `Real` | One of the actions listed under "Other" |
| `ev_step` | `Real` | Step event |
| `ev_trigger` ⚠️obsoleta | `Real` |  |

### ExternalArgumentType

| Constante | Tipo | Descripción |
|---|---|---|
| `ty_real` | `Real` | A real number argument |
| `ty_string` | `Real` | a null-terminated string argument |

### ExternalCallType

| Constante | Tipo | Descripción |
|---|---|---|
| `dll_cdecl` | `Real` | This is the default C, C++ call |
| `dll_stdcall` | `Real` | This is the standard WinAPI call (Windows dll only) |

### FileAttribute

| Constante | Tipo | Descripción |
|---|---|---|
| `fa_archive` | `Real` | Archived files |
| `fa_directory` | `Real` | Directories |
| `fa_hidden` | `Real` | Hidden files |
| `fa_none` | `Real` | No file filter |
| `fa_readonly` | `Real` | Read-only files |
| `fa_sysfile` | `Real` | System files |
| `fa_volumeid` | `Real` | Volume-id files |

### GameSpeed

| Constante | Tipo | Descripción |
|---|---|---|
| `gamespeed_fps` | `Real` | Gets the game speed using frames per second. |
| `gamespeed_microseconds` | `Real` | Gets the game speed using microseconds per frame. |

### GamepadAxis

| Constante | Tipo | Descripción |
|---|---|---|
| `gp_axis_acceleration_x` | `Real` | The gamepad's acceleration on the X axis |
| `gp_axis_acceleration_y` | `Real` | The gamepad's acceleration on the Y axis |
| `gp_axis_acceleration_z` | `Real` | The gamepad's acceleration on the Z axis |
| `gp_axis_angular_velocity_x` | `Real` | The gamepad's angular velocity on the X axis |
| `gp_axis_angular_velocity_y` | `Real` | The gamepad's angular velocity on the Y axis |
| `gp_axis_angular_velocity_z` | `Real` | The gamepad's angular velocity on the Z axis |
| `gp_axis_orientation_w` | `Real` | The gamepad's W orientation |
| `gp_axis_orientation_x` | `Real` | The gamepad's X orientation |
| `gp_axis_orientation_y` | `Real` | The gamepad's Y orientation |
| `gp_axis_orientation_z` | `Real` | The gamepad's Z orientation |
| `gp_axislh` | `Real` | Left stick horizontal axis (analog) |
| `gp_axislv` | `Real` | Left stick vertical axis (analog) |
| `gp_axisrh` | `Real` | Right stick horizontal axis (analog) |
| `gp_axisrv` | `Real` | Right stick vertical axis (analog) |

### GamepadButton

| Constante | Tipo | Descripción |
|---|---|---|
| `gp_extra1` | `Real` | A gamepad button used for mapping extra buttons on a device |
| `gp_extra2` | `Real` | A gamepad button used for mapping extra buttons on a device |
| `gp_extra3` | `Real` | A gamepad button used for mapping extra buttons on a device |
| `gp_extra4` | `Real` | A gamepad button used for mapping extra buttons on a device |
| `gp_extra5` | `Real` | A gamepad button used for mapping extra buttons on a device |
| `gp_extra6` | `Real` | A gamepad button used for mapping extra buttons on a device |
| `gp_face1` | `Real` | Top button 1 (this maps to the A" on an Xbox 360 controller and the cross on a PS controller) |
| `gp_face2` | `Real` | Top button 2 (this maps to the B" on an Xbox 360 controller and the circle on a PS controller) |
| `gp_face3` | `Real` | Top button 3 (this maps to the X" on an Xbox 360 controller and the square on a PS controller) |
| `gp_face4` | `Real` | Top button 4 (this maps to the Y" on an Xbox 360 controller and the triangle on a PS controller) |
| `gp_home` | `Real` | The gamepad's Home button |
| `gp_padd` | `Real` | D-pad down |
| `gp_paddlel` | `Real` | A gamepad button used for mapping paddle left button on a device |
| `gp_paddlelb` | `Real` | A gamepad button used for mapping paddle left bottom button on a device |
| `gp_paddler` | `Real` | A gamepad button used for mapping paddle right button on a device |
| `gp_paddlerb` | `Real` | A gamepad button used for mapping paddle right bottom button on a device |
| `gp_padl` | `Real` | D-pad left |
| `gp_padr` | `Real` | D-pad right |
| `gp_padu` | `Real` | D-pad up |
| `gp_select` | `Real` | The select button (on a DS4 controller, this triggers when you press the touchpad down) |
| `gp_shoulderl` | `Real` | Left shoulder button |
| `gp_shoulderlb` | `Real` | Left shoulder trigger |
| `gp_shoulderr` | `Real` | Right shoulder button |
| `gp_shoulderrb` | `Real` | Right shoulder trigger |
| `gp_start` | `Real` | The start button (this is the "options" button on a PS4 controller) |
| `gp_stickl` | `Real` | The left stick pressed (as a button) |
| `gp_stickr` | `Real` | The right stick pressed (as a button) |
| `gp_touchpadbutton` | `Real` | A gamepad button used for mapping the touchpad button on a device (i.e. PS4 and PS5) |

### HAlign

| Constante | Tipo | Descripción |
|---|---|---|
| `fa_center` | `Real` |  |
| `fa_left` | `Real` |  |
| `fa_right` | `Real` |  |

### LayerElementType

| Constante | Tipo | Descripción |
|---|---|---|
| `layerelementtype_background` | `Real` | The element is a background. |
| `layerelementtype_instance` | `Real` | The element is an instance. |
| `layerelementtype_oldtilemap` | `Real` | The element is an old type tilemap. |
| `layerelementtype_particlesystem` | `Real` | The element is a particle system. |
| `layerelementtype_sequence` | `Real` | The element is a sequence asset. |
| `layerelementtype_sprite` | `Real` | The element is a sprite asset. |
| `layerelementtype_text` | `Real` | The element is a text element. |
| `layerelementtype_tile` | `Real` | The element is a legacy background tile (this is only valid for projects that have been imported from previous versions of GameMaker). |
| `layerelementtype_tilemap` | `Real` | The element is a tilemap. |
| `layerelementtype_undefined` | `Real` | The element does not exist or the ID value is erroneous. |

### LayerType

| Constante | Tipo | Descripción |
|---|---|---|
| `layer_type_room` | `Real` | A layer of room type. |
| `layer_type_ui_display` | `Real` | A ui layer using display space. |
| `layer_type_ui_viewports` | `Real` | A ui layer using viewports space. |
| `layer_type_unknown` | `Real` | Unknown layer type. |

### LightType

| Constante | Tipo | Descripción |
|---|---|---|
| `lighttype_dir` | `Real` | The light is a directional light |
| `lighttype_point` | `Real` | The light is a point light |

### MatrixType

| Constante | Tipo | Descripción |
|---|---|---|
| `matrix_projection` | `Real` | The current projection matrix |
| `matrix_view` | `Real` | The current view matrix |
| `matrix_world` | `Real` | The current world matrix |

### MouseButton

| Constante | Tipo | Descripción |
|---|---|---|
| `m_axisx` | `Real` | Mouse x-axis position in room coordinates |
| `m_axisx_gui` | `Real` | Mouse x-axis position in GUI coordinates |
| `m_axisy` | `Real` | Mouse y-axis position in room coordinates |
| `m_axisy_gui` | `Real` | Mouse y-axis position in GUI coordinates |
| `m_scroll_down` | `Real` | Mouse scroll direction down |
| `m_scroll_up` | `Real` | Mouse scroll direction up |
| `mb_any` | `Real` | Any of the mouse buttons |
| `mb_left` | `Real` | The left mouse button |
| `mb_middle` | `Real` | The middle mouse button (this may not be valid for all target platforms) |
| `mb_none` | `Real` | No mouse button |
| `mb_right` | `Real` | The right mouse button |
| `mb_side1` | `Real` | Mouse side button 1 |
| `mb_side2` | `Real` | Mouse side button 2 |

### NetworkConfig

| Constante | Tipo | Descripción |
|---|---|---|
| `network_config_avoid_time_wait` | `Real` | Sets the SO_LINGER timeout value to 0 for an exisiting TCP socket |
| `network_config_connect_timeout` | `Real` | Set a connection timeout value |
| `network_config_disable_multicast` | `Real` | Disables use of IPv6 multicast for broadcast discovery on a UDP socket. |
| `network_config_disable_reliable_udp` | `Real` | Disables the "reliable UDP" protocol for an existing UDP socked. |
| `network_config_enable_multicast` | `Real` | Enables use of IPv6 multicast for broadcast discovery on a UDP socket. |
| `network_config_enable_reliable_udp` | `Real` | Enables the "reliable UDP" protocol for an existing UDP socket |
| `network_config_message_size_limit` | `Real` | Set the size limit for buffered incoming messages, size is an integer number of bytes as 3rd parameter |
| `network_config_use_non_blocking_socket` | `Real` | Tell GameMaker not to block on connect. |
| `network_config_websocket_protocol` | `Real` | Set the protocol to use on websocket upgrade message, protocol is a string as 3rd parameter |

### NetworkConnectType

| Constante | Tipo | Descripción |
|---|---|---|
| `network_connect_active` | `Real` | This will actively prompt the user to fix the connection, if it failed. |
| `network_connect_blocking` | `Real` | This attempts to connect and blocks execution while trying. |
| `network_connect_nonblocking` | `Real` | This will actively prompt the user to fix the connection, if it failed. |
| `network_connect_none` | `Real` | This does not attempt to connect. |
| `network_connect_passive` | `Real` | This will try to connect and silently fail if no successful connection could be established. |

### NetworkType

| Constante | Tipo | Descripción |
|---|---|---|
| `network_type_connect` | `Real` | The event was triggered by a connection. |
| `network_type_data` | `Real` | The event was triggered by incoming data. |
| `network_type_disconnect` | `Real` | The event was triggered by a disconnection. |
| `network_type_down` | `Real` | The network went down. |
| `network_type_non_blocking_connect` | `Real` | The event was triggered by a connection configured as non-blocking. |
| `network_type_up` | `Real` | The connection succeeded. |
| `network_type_up_failed` | `Real` | The connection failed. |

### NineSlice

| Constante | Tipo | Descripción |
|---|---|---|
| `nineslice_blank` | `Real` | The slice will not be stretched or repeated, resulting in a blank area after it |
| `nineslice_bottom` | `Real` | The bottom edge slice |
| `nineslice_center` | `Real` | The center slice |
| `nineslice_centre` | `Real` | The centre slice |
| `nineslice_hide` | `Real` | The slice will not appear at all |
| `nineslice_left` | `Real` | The left edge slice |
| `nineslice_mirror` | `Real` | The slice will be repeated by mirroring |
| `nineslice_repeat` | `Real` | The slice will be repeated |
| `nineslice_right` | `Real` | The right edge slice |
| `nineslice_stretch` | `Real` | The slice will be stretched |
| `nineslice_top` | `Real` | The top edge slice |
| `texturegroup_status_fetched` | `Real` | The texture group is decompressed and ready to be used |
| `texturegroup_status_loaded` | `Real` | The texture group is loaded |
| `texturegroup_status_loading` | `Real` | The texture group is loading |
| `texturegroup_status_unloaded` | `Real` | The texture group is unloaded |

### OperatingSystem

| Constante | Tipo | Descripción |
|---|---|---|
| `os_android` | `Real` | Android |
| `os_gdk` | `Real` | Microsoft GDK platform (Xbox One and Series X/S) |
| `os_gxgames` | `Real` | GX.games |
| `os_ios` | `Real` | iOS (iPhone, iPad, iPod Touch) |
| `os_linux` | `Real` | Linux |
| `os_macosx` | `Real` | macOS X |
| `os_operagx` | `Real` | Opera GX |
| `os_ps3` ⚠️obsoleta | `Real` |  |
| `os_ps4` | `Real` | Sony PlayStation 4 |
| `os_ps5` | `Real` | Sony PlayStation 5 |
| `os_psvita` ⚠️obsoleta | `Real` |  |
| `os_switch` | `Real` | Nintendo Switch |
| `os_switch2` | `Real` | Nintendo Switch 2 |
| `os_tvos` | `Real` | Apple tvOS |
| `os_unknown` | `Real` | Unknown OS |
| `os_uwp` ⚠️obsoleta | `Real` | Windows 10 Universal Windows Platform |
| `os_win32` ⚠️obsoleta | `Real` |  |
| `os_win8native` ⚠️obsoleta | `Real` |  |
| `os_windows` | `Real` | Windows OS |
| `os_winphone` ⚠️obsoleta | `Real` |  |
| `os_xboxone` ⚠️obsoleta | `Real` | Microsoft Xbox One |
| `os_xboxseriesxs` | `Real` | Microsoft Xbox Series X/S |

### ParticleDistribution

| Constante | Tipo | Descripción |
|---|---|---|
| `ps_distr_gaussian` | `Real` | A gaussian distribution where more particles are generated in the center rather than the edges. |
| `ps_distr_invgaussian` | `Real` | An inverse gaussian distribution where more particles are generated at the edges than center. |
| `ps_distr_linear` | `Real` | A Linear distribution where all particles have an equal chance of appearing anywhere in the area. |

### ParticleEmitterMode

| Constante | Tipo | Descripción |
|---|---|---|
| `ps_mode_burst` | `Real` | Emitter burst particles just once. |
| `ps_mode_stream` | `Real` | Emitter streams new particles each frame. |

### ParticleRegionShape

| Constante | Tipo | Descripción |
|---|---|---|
| `ps_shape_diamond` | `Real` | A diamond shape with the points at half width and half height. |
| `ps_shape_ellipse` | `Real` | An ellipse, with the width and height defined by the area. |
| `ps_shape_line` | `Real` | A single line, where the start point is the left and top and the end point is the right and bottom. |
| `ps_shape_rectangle` | `Real` | A rectangular shape that fills the given area. |

### ParticleShape

| Constante | Tipo | Descripción |
|---|---|---|
| `pt_shape_circle` | `Real` | A 3px outlined circle. |
| `pt_shape_cloud` | `Real` | A thin cloud, requires up scaling and multiple particles to resemble a cloud. |
| `pt_shape_disk` | `Real` | A filled circle. |
| `pt_shape_explosion` | `Real` | A squarish cloud of smoke. requires multiple colours to resemble an explosion. |
| `pt_shape_flare` | `Real` | A harshly glowing point (looks like an actual star in the night). |
| `pt_shape_line` | `Real` | An 8px wide horizontal line. |
| `pt_shape_pixel` | `Real` | A 1x1 pixel. (This is the default setting.) |
| `pt_shape_ring` | `Real` | A circle with an inward glow (looks like a bubble). |
| `pt_shape_smoke` | `Real` | A smooth version of the explosion effect. Use multiple to create a smoke cloud. |
| `pt_shape_snow` | `Real` | A generic snowflake shape. |
| `pt_shape_spark` | `Real` | A spark effect, like a star with multiple points fading out. |
| `pt_shape_sphere` | `Real` | A circle with an outward glow, solid in the middle, glowing outwards. |
| `pt_shape_square` | `Real` | A filled square. |
| `pt_shape_star` | `Real` | A five-point filled star. |

### PathAction

| Constante | Tipo | Descripción |
|---|---|---|
| `path_action_continue` | `Real` | Continue from the current position |
| `path_action_restart` | `Real` | Continue the path from the start, jumping to the start position again if the path is not closed |
| `path_action_reverse` | `Real` | Go backwards along the path again (achieved by reversing the path movement speed) |
| `path_action_stop` | `Real` | End the path |

### PhysicsDebugFlag

| Constante | Tipo | Descripción |
|---|---|---|
| `phy_debug_render_aabb` | `Real` | This shows the absolute bounding box of each fixture in relation to the room axis. |
| `phy_debug_render_collision_pairs` | `Real` | This will show any fixtures that are currently in collision. |
| `phy_debug_render_coms` | `Real` | This marks the center of mass of each fixture in the room. |
| `phy_debug_render_core_shapes` | `Real` | Shows the basic shapes that make up the fixtures in the room. |
| `phy_debug_render_joints` | `Real` | This will draw each of the joints of all fixtures in the room. |
| `phy_debug_render_obb` | `Real` | This shows the relative bounding box for the fixtures in the room. |
| `phy_debug_render_shapes` | `Real` | This shows the actual shapes that make up fixtures within the room. |

### PhysicsJointProperty

| Constante | Tipo | Descripción |
|---|---|---|
| `phy_joint_anchor_1_x` | `Real` | The x coordinate of the first anchor point of the joint in the room |
| `phy_joint_anchor_1_y` | `Real` | The y coordinate of the first anchor point of the joint in the room |
| `phy_joint_anchor_2_x` | `Real` | The x coordinate of the second anchor point of the joint in the room |
| `phy_joint_anchor_2_y` | `Real` | The y coordinate of the second anchor point of the joint in the room |
| `phy_joint_angle` | `Real` | The angle that a line between the two anchor points of the joint makes. This is calculated using the physics world coordinates (not the GameMaker room coordinates) in radians. |
| `phy_joint_angle_limits` | `Real` | Enable or disable angle limiting for the joint. Set the value to true to enable or false to disable. |
| `phy_joint_damping_ratio` | `Real` | The damping ratio is non-dimensional and defines the "springiness" of the joint. The value for this constant is typically between 0 and 1, but can be larger, and at 1, the damping  |
| `phy_joint_frequency` | `Real` | This will return (or set) the oscillation frequency for the joint, in hertz, and typically the frequency should be less than a half the frequency of the time step, as set by the fu |
| `phy_joint_length_1` | `Real` | This will return the length of the joint from the first local x/y coordinates to the first anchor x/y coordinates (Distance joints only, can only be read from) |
| `phy_joint_length_2` | `Real` | This will return the length of the joint from the second local x/y coordinates to the second anchor x/y coordinates (Distance joints only, can only be written to) |
| `phy_joint_lower_angle_limit` | `Real` | The lower angle limit for the joint in degrees. |
| `phy_joint_max_force` | `Real` | The maximum force value for the joint. |
| `phy_joint_max_length` | `Real` | The maximum extension for the connection between the two anchor points. |
| `phy_joint_max_motor_force` | `Real` | The value specified when the joint was created for the maximum motor force |
| `phy_joint_max_motor_torque` | `Real` | The value specified when the joint was created for the maximum motor torque |
| `phy_joint_max_torque` | `Real` | The maximum torque value for the joint. |
| `phy_joint_motor_force` | `Real` | The current motor force |
| `phy_joint_motor_speed` | `Real` | The current motor speed |
| `phy_joint_motor_torque` | `Real` | The current motor torque |
| `phy_joint_reaction_force_x` | `Real` | This is the reaction force being applied to the second instance in a joint at the x anchor position |
| `phy_joint_reaction_force_y` | `Real` | This is the reaction force being applied to the second instance in a joint at the y anchor position |
| `phy_joint_reaction_torque` | `Real` | This is the torque being applied to the second instance in a joint at the anchor position |
| `phy_joint_speed` | `Real` | The current joint movement speed. |
| `phy_joint_translation` | `Real` | Gets the distance between the anchor x/y coordinates and the local x/y coordinates. |
| `phy_joint_upper_angle_limit` | `Real` | The upper angle limit for the joint in degrees. |

### PhysicsParticleDataFlag

| Constante | Tipo | Descripción |
|---|---|---|
| `phy_particle_data_flag_category` | `Real` | The particle category (as defined when you created the particle or group to which it belongs). |
| `phy_particle_data_flag_colour` | `Real` | The colour and alpha value (hexadecimal). |
| `phy_particle_data_flag_position` | `Real` | The x and y position of the particle. |
| `phy_particle_data_flag_typeflags` | `Real` | The flags value for the particle. |
| `phy_particle_data_flag_velocity` | `Real` | The horizontal and vertical speed. |

### PhysicsParticleFlag

| Constante | Tipo | Descripción |
|---|---|---|
| `phy_particle_data_flag_color` | `Real` | The color and alpha value (hexadecimal). |
| `phy_particle_flag_colormixing` | `Real` | Color-mixing particles take on some of the color of other particles with which they collide. Note that if only one of the two colliding particles is a color-mixing one, the other p |
| `phy_particle_flag_colourmixing` | `Real` | Colour-mixing particles take on some of the colour of other particles with which they collide. Note that if only one of the two colliding particles is a colour-mixing one, the othe |
| `phy_particle_flag_elastic` | `Real` | Elastic particles deform and may also bounce when they collide with other rigid bodies in the physics simulation. |
| `phy_particle_flag_powder` | `Real` | Powder particles produce a scattering effect such as you might see with sand or dust. |
| `phy_particle_flag_spring` | `Real` | Spring particles produce the effect of being attached to one another, as if by a spring. Particles created with this flag are "connected" in pairs, with each particle being connect |
| `phy_particle_flag_tensile` | `Real` | Tensile particles are used to produce the effect of surface tension, or the taut curvature on the surface of a body of liquid. They might be used, for example, to create the surfac |
| `phy_particle_flag_viscous` | `Real` | A viscous particle is one that exhibits "clinginess" or "stickiness", like oil. Viscous particles will clump and stick together more. |
| `phy_particle_flag_wall` | `Real` | This defines the particle as static, essentially creating it as an immovable object in the physics simulation, as they will remain in a fixed position no matter what collides with  |
| `phy_particle_flag_water` | `Real` | The default properties for a soft body particle. |
| `phy_particle_flag_zombie` | `Real` | A zombie particle is one that will be destroyed after a single step with all others flagged in this way. |

### PhysicsParticleGroupFlag

| Constante | Tipo | Descripción |
|---|---|---|
| `phy_particle_group_flag_rigid` | `Real` | Rigid particle groups are ones whose shape does not change, even when they collide with other fixtures. |
| `phy_particle_group_flag_solid` | `Real` | A solid particle group prevents other fixtures from lodging inside of it. Should anything penetrate it, the solid particle group pushes the offending fixture back out to its surfac |

### PrimitiveType

| Constante | Tipo | Descripción |
|---|---|---|
| `pr_linelist` | `Real` | A line list - A line is drawn between the first and the second vertex, between the third and fourth vertex, etc. |
| `pr_linestrip` | `Real` | A line strip - A line is drawn between the first and the second vertex, between the second and the third vertex, the third and the fourth vertex, etc. |
| `pr_pointlist` | `Real` | A point list - A point is drawn for every vertex. |
| `pr_trianglefan` | `Real` | A triangle fan - Every two vertices connect to the first vertex to make a triangle. |
| `pr_trianglelist` | `Real` | A triangle list - A triangle is drawn for the first, second and third vertex, then for the fourth, fifth and sixth vertex, etc. |
| `pr_trianglestrip` | `Real` | A triangle strip - A triangle is drawn for the first, second and third vertex, then for the second, third and fourth vertex, etc. |

### SeekOffset

| Constante | Tipo | Descripción |
|---|---|---|
| `buffer_seek_end` | `Real` | The end of the buffer |
| `buffer_seek_relative` | `Real` | A position relative to the current read/write position |
| `buffer_seek_start` | `Real` | The start of the buffer |

### SendOption

| Constante | Tipo | Descripción |
|---|---|---|
| `network_send_binary` | `Real` | Send a BINARY message over WeSocket |
| `network_send_text` | `Real` | Send a TEXT message over WebSocket |

### SequenceAudioKey

| Constante | Tipo | Descripción |
|---|---|---|
| `seqaudiokey_loop` | `Real` | The sound will loop when played. |
| `seqaudiokey_oneshot` | `Real` | The sound will only play once then stop. |

### SequenceDirection

| Constante | Tipo | Descripción |
|---|---|---|
| `seqdir_left` | `Real` | The sequence will play frames in a decremental order from right to left |
| `seqdir_right` | `Real` | The sequence will play frames in an incremental order from left to right |

### SequencePlay

| Constante | Tipo | Descripción |
|---|---|---|
| `seqplay_loop` | `Real` | The sequence will loop, with the playhead going back to the start when it reaches the end of the playback region. |
| `seqplay_oneshot` | `Real` | The sequence will play once then stop when finished. |
| `seqplay_pingpong` | `Real` | The sequence will loop, with the playhead reversing direction when it reaches the end of the playback region. |

### SequenceTextKey

| Constante | Tipo | Descripción |
|---|---|---|
| `seqtextkey_bottom` | `Real` | The text will be vertically aligned to the bottom of the frame. |
| `seqtextkey_center` | `Real` | The text will be center-aligned. |
| `seqtextkey_justify` | `Real` | The text will be justified. |
| `seqtextkey_left` | `Real` | The text will be left-aligned. |
| `seqtextkey_middle` | `Real` | The text will be vertically aligned to the middle of the frame. |
| `seqtextkey_right` | `Real` | The text will be right-aligned. |
| `seqtextkey_top` | `Real` | The text will be vertically aligned to the top of the frame. |

### SequenceTrackType

| Constante | Tipo | Descripción |
|---|---|---|
| `seqtracktype_audio` | `Real` | This is an audio asset track. |
| `seqtracktype_audioeffect` | `Real` | This is an audio effect parameter track. |
| `seqtracktype_bool` | `Real` | Not used currently. |
| `seqtracktype_clipmask` | `Real` | This is a clip mask group asset track. |
| `seqtracktype_clipmask_mask` | `Real` | This is a clip mask sprite asset track used for generating the clip mask. |
| `seqtracktype_clipmask_subject` | `Real` | This is a clip mask sprite asset track that is being masked. |
| `seqtracktype_color` | `Real` | This is a color data parameter track. |
| `seqtracktype_colour` | `Real` | This is a colour data parameter track. |
| `seqtracktype_empty` | `Real` | Not used currently. |
| `seqtracktype_graphic` | `Real` | This is a graphics (sprite) asset track. |
| `seqtracktype_group` | `Real` | This is a group folder asset track. |
| `seqtracktype_instance` | `Real` | This is an instance asset track. |
| `seqtracktype_message` | `Real` | This is a broadcast message track. |
| `seqtracktype_moment` | `Real` | This is an event/moment track. |
| `seqtracktype_particlesystem` | `Real` | This is a particle system asset track. |
| `seqtracktype_real` | `Real` | This is a real number value parameter track. |
| `seqtracktype_sequence` | `Real` | This is a sequence asset track. |
| `seqtracktype_spriteframes` | `Real` | Not used currently. |
| `seqtracktype_string` | `Real` | Not used currently. |
| `seqtracktype_text` | `Real` | This is a text track. |

### SocketType

| Constante | Tipo | Descripción |
|---|---|---|
| `network_socket_bluetooth` | `Real` | Create a Bluetooth socket (currently unavailable!). |
| `network_socket_tcp` | `Real` | Create a socket using TCP. |
| `network_socket_udp` | `Real` | Create a socket using UDP. |
| `network_socket_ws` | `Real` | Create a web socket (only for connecting to HTML5 projects), using TCP. |
| `network_socket_wss` | `Real` | Create a socket using Secure Websockets. |

### SpriteSpeed

| Constante | Tipo | Descripción |
|---|---|---|
| `spritespeed_framespergameframe` | `Real` | Specifies that playbackSpeed should be interpreted as frames-per-game-frame. |
| `spritespeed_framespersecond` | `Real` | Specifies that playbackSpeed should be interpreted as frames-per-second |

### StencilOp

| Constante | Tipo | Descripción |
|---|---|---|
| `stencilop_decr` | `Real` | Decrements the stencil buffer value, clamping at 0. |
| `stencilop_decr_wrap` | `Real` | Decrements the stencil buffer value, wrapping to the maximum value at 0. |
| `stencilop_incr` | `Real` | Increments the stencil buffer value, clamping at the maximum value. |
| `stencilop_incr_wrap` | `Real` | Increments the stencil buffer value, wrapping to 0 at the maximum value. |
| `stencilop_invert` | `Real` | Performs a bitwise inversion on the current stencil buffer value. |
| `stencilop_keep` | `Real` | Keeps the current value in the stencil buffer. |
| `stencilop_replace` | `Real` | Sets the stencil buffer value to the stencil reference value. |
| `stencilop_zero` | `Real` | Sets the stencil buffer value to 0. |

### SurfaceFormatType

| Constante | Tipo | Descripción |
|---|---|---|
| `surface_r16float` | `Real` | 16 bit float single channel surface format |
| `surface_r32float` | `Real` | 32 bit float single channel surface format |
| `surface_r8unorm` | `Real` | 8 bit integer single channel (normalised) surface format |
| `surface_rg8unorm` | `Real` | 8 bit integer two channel (normalised) surface format |
| `surface_rgba16float` | `Real` | 16 bit float per channel RGBA surface format |
| `surface_rgba32float` | `Real` | 32 bit float per channel RGBA surface format |
| `surface_rgba4unorm` | `Real` | 4 bit integer per channel (normalised) RGBA surface format |
| `surface_rgba8unorm` | `Real` | 8 bit integer per channel (normalised) RGBA surface format |

### TextAlign

| Constante | Tipo | Descripción |
|---|---|---|
| `textalign_bottom` | `Real` | Indicates that text should be aligned to the bottom of the frame. |
| `textalign_center` | `Real` | Indicates that text should be centred horizontally within the frame. |
| `textalign_justify` | `Real` | Indicates that text should be justified within the frame. |
| `textalign_left` | `Real` | Indicates that text should be aligned to the left of the frame. |
| `textalign_middle` | `Real` | Indicates that text should be centered vertically within the frame. |
| `textalign_right` | `Real` | Indicates that text should be aligned to the right of the frame. |
| `textalign_top` | `Real` | Indicates that text should be aligned to the top of the frame. |

### TextOrigin

| Constante | Tipo | Descripción |
|---|---|---|
| `origin_bottomcentre` | `Real` | Bottom centre of the text frame |
| `origin_bottomleft` | `Real` | Bottom left of the text frame |
| `origin_bottomright` | `Real` | Bottom right of the text frame |
| `origin_middlecentre` | `Real` | Middle centre of the text frame |
| `origin_middleleft` | `Real` | Middle left of the text frame |
| `origin_middleright` | `Real` | Middle right of the text frame |
| `origin_topcentre` | `Real` | Top centre of the text frame |
| `origin_topleft` | `Real` | Top left of the text frame |
| `origin_topright` | `Real` | Top right of the text frame |

### TextWrap

| Constante | Tipo | Descripción |
|---|---|---|
| `textwrap_default` | `Real` | Default text wrapping mode. |
| `textwrap_splitwords` | `Real` | Text wrapping split words to the next line when too long to fit the frame width |

### TileMask

| Constante | Tipo | Descripción |
|---|---|---|
| `tile_flip` | `Real` | Used to set/get the flip bit of a tile data blob. |
| `tile_index_mask` | `Real` | A special constant that is for "and"-ing with the tile data blob to extract the tile index. |
| `tile_mirror` | `Real` | Used to set/get the mirror bit of a tile data blob. |
| `tile_rotate` | `Real` | Used to set/get the rotate bit of a tile data blob. |

### TimeSource

| Constante | Tipo | Descripción |
|---|---|---|
| `time_source_game` | `Real` | The game time source |
| `time_source_global` | `Real` | The global time source |

### TimeSourceExpiryType

| Constante | Tipo | Descripción |
|---|---|---|
| `time_source_expire_after` | `Real` | The time source will expire on the first frame after its expiry time |
| `time_source_expire_nearest` | `Real` | The time source will expire on the frame nearest to its expiry time |

### TimeSourceState

| Constante | Tipo | Descripción |
|---|---|---|
| `time_source_state_active` | `Real` | The time source has been started and is counting down |
| `time_source_state_initial` | `Real` | The time source has not been started yet |
| `time_source_state_paused` | `Real` | The time source is paused |
| `time_source_state_stopped` | `Real` | The time source was stopped or it completely expired |

### TimeSourceUnits

| Constante | Tipo | Descripción |
|---|---|---|
| `time_source_units_frames` | `Real` | Use frames for the time source period (frame-dependent) |
| `time_source_units_seconds` | `Real` | Use seconds for the time source period (frame-independent) |

### TimingMethod

| Constante | Tipo | Descripción |
|---|---|---|
| `tm_countvsyncs` | `Real` | Vsync timing is the main timing method (default for all supported platforms) |
| `tm_countvsyncs_winalt` | `Real` | This is a windows-specific timing method which may improve consistency |
| `tm_sleep` | `Real` | The sleep margin value is the main timing method |
| `tm_systemtiming` | `Real` | Ignore gamespeed and allow the system to control framerate |

### VAlign

| Constante | Tipo | Descripción |
|---|---|---|
| `fa_bottom` | `Real` |  |
| `fa_middle` | `Real` |  |
| `fa_top` | `Real` |  |

### VertexType

| Constante | Tipo | Descripción |
|---|---|---|
| `vertex_type_color` | `Real` | Four component values (r, g, b, a) |
| `vertex_type_colour` | `Real` | Four component values (r, g, b, a) |
| `vertex_type_float1` | `Real` | A single floating point value |
| `vertex_type_float2` | `Real` | Two floating point values |
| `vertex_type_float3` | `Real` | Three floating point values |
| `vertex_type_float4` | `Real` | Four floating point values |
| `vertex_type_ubyte4` | `Real` | Four component unsigned byte values (from 0 to 255) |

### VertexUsage

| Constante | Tipo | Descripción |
|---|---|---|
| `vertex_usage_binormal` | `Real` | binormal values |
| `vertex_usage_blendindices` | `Real` | the indices of the matrices to use (for skeletal animation, for example) |
| `vertex_usage_blendweight` | `Real` | the blendweight of the input matrix (for skeletal animation, for example) |
| `vertex_usage_color` | `Real` | color values (r, g, b, a) |
| `vertex_usage_colour` | `Real` | colour values (r, g, b, a) |
| `vertex_usage_depth` | `Real` | vertex depth buffer value |
| `vertex_usage_fog` | `Real` | fog values |
| `vertex_usage_normal` | `Real` | vertex normal values (nx, ny, nz) |
| `vertex_usage_position` | `Real` | position values (x, y, z) |
| `vertex_usage_psize` | `Real` |  |
| `vertex_usage_sample` | `Real` | sampler index |
| `vertex_usage_tangent` | `Real` | tangent values |
| `vertex_usage_texcoord` | `Real` | UV coordinates (u, v) |
| `vertex_usage_textcoord` ⚠️obsoleta | `Real` | UV coordinates (u, v) |

### VideoFormat

| Constante | Tipo | Descripción |
|---|---|---|
| `video_format_rgba` | `Real` | The video surface uses the RGBA color model |
| `video_format_yuv` | `Real` | The video surface uses the YUV color model |

### VideoStatus

| Constante | Tipo | Descripción |
|---|---|---|
| `video_status_closed` | `Real` | No video is currently loaded, or the video was closed with video_close() |
| `video_status_paused` | `Real` | The video is paused |
| `video_status_playing` | `Real` | The video is currently playing |
| `video_status_preparing` | `Real` | The video is currently preparing and has not started playing yet |

### VirtualKey

| Constante | Tipo | Descripción |
|---|---|---|
| `vk_add` | `Real` | add key on the numeric keypad |
| `vk_alt` | `Real` | alt key |
| `vk_anykey` | `Real` | keycode representing that any key is pressed |
| `vk_backspace` | `Real` | backspace key |
| `vk_control` | `Real` | either of the control keys |
| `vk_decimal` | `Real` | decimal dot keys on the numeric keypad |
| `vk_delete` | `Real` | delete key |
| `vk_divide` | `Real` | divide key on the numeric keypad |
| `vk_down` | `Real` | keycode for the down arrow key |
| `vk_end` | `Real` | end key |
| `vk_enter` | `Real` | enter key |
| `vk_escape` | `Real` | escape key |
| `vk_f1` | `Real` | keycode for the function keys F1 to F12 |
| `vk_f10` | `Real` |  |
| `vk_f11` | `Real` |  |
| `vk_f12` | `Real` |  |
| `vk_f2` | `Real` |  |
| `vk_f3` | `Real` |  |
| `vk_f4` | `Real` |  |
| `vk_f5` | `Real` |  |
| `vk_f6` | `Real` |  |
| `vk_f7` | `Real` |  |
| `vk_f8` | `Real` |  |
| `vk_f9` | `Real` |  |
| `vk_home` | `Real` | home key |
| `vk_insert` | `Real` | insert key |
| `vk_lalt` | `Real` | left alt key |
| `vk_lcontrol` | `Real` | left control key |
| `vk_left` | `Real` | keycode for the left arrow key |
| `vk_lshift` | `Real` | left shift key |
| `vk_multiply` | `Real` | multiply key on the numeric keypad |
| `vk_nokey` | `Real` | keycode representing that no key is pressed |
| `vk_numpad0` | `Real` | number keys on the numeric keypad |
| `vk_numpad1` | `Real` |  |
| `vk_numpad2` | `Real` |  |
| `vk_numpad3` | `Real` |  |
| `vk_numpad4` | `Real` |  |
| `vk_numpad5` | `Real` |  |
| `vk_numpad6` | `Real` |  |
| `vk_numpad7` | `Real` |  |
| `vk_numpad8` | `Real` |  |
| `vk_numpad9` | `Real` |  |
| `vk_pagedown` | `Real` | pagedown key |
| `vk_pageup` | `Real` | pageup key |
| `vk_pause` | `Real` | pause/break key |
| `vk_printscreen` | `Real` | printscreen/sysrq key |
| `vk_ralt` | `Real` | right alt key |
| `vk_rcontrol` | `Real` | right control key |
| `vk_return` | `Real` |  |
| `vk_right` | `Real` | keycode for the right arrow key |
| `vk_rshift` | `Real` | right shift key |
| `vk_shift` | `Real` | either of the shift keys |
| `vk_space` | `Real` | space key |
| `vk_subtract` | `Real` | subtract key on the numeric keypad |
| `vk_tab` | `Real` | tab key |
| `vk_up` | `Real` | keycode for the up arrow key |

### VirtualKeyboardAutoCapitalizeType

| Constante | Tipo | Descripción |
|---|---|---|
| `kbv_autocapitalize_characters` | `Real` |  |
| `kbv_autocapitalize_none` | `Real` |  |
| `kbv_autocapitalize_sentences` | `Real` |  |
| `kbv_autocapitalize_words` | `Real` |  |

### VirtualKeyboardReturnType

| Constante | Tipo | Descripción |
|---|---|---|
| `kbv_returnkey_continue` | `Real` |  |
| `kbv_returnkey_default` | `Real` |  |
| `kbv_returnkey_done` | `Real` |  |
| `kbv_returnkey_emergency` | `Real` |  |
| `kbv_returnkey_go` | `Real` |  |
| `kbv_returnkey_google` | `Real` |  |
| `kbv_returnkey_join` | `Real` |  |
| `kbv_returnkey_next` | `Real` |  |
| `kbv_returnkey_route` | `Real` |  |
| `kbv_returnkey_search` | `Real` |  |
| `kbv_returnkey_send` | `Real` |  |
| `kbv_returnkey_yahoo` | `Real` |  |

### VirtualKeyboardType

| Constante | Tipo | Descripción |
|---|---|---|
| `kbv_type_ascii` | `Real` |  |
| `kbv_type_default` | `Real` |  |
| `kbv_type_email` | `Real` |  |
| `kbv_type_numbers` | `Real` |  |
| `kbv_type_phone` | `Real` |  |
| `kbv_type_phone_name` | `Real` |  |
| `kbv_type_url` | `Real` |  |

### ZFunction

| Constante | Tipo | Descripción |
|---|---|---|
| `cmpfunc_always` | `Real` | Always |
| `cmpfunc_equal` | `Real` | Equal |
| `cmpfunc_greater` | `Real` | Greater |
| `cmpfunc_greaterequal` | `Real` | Greater or Equal |
| `cmpfunc_less` | `Real` | Less |
| `cmpfunc_lessequal` | `Real` | Less or Equal |
| `cmpfunc_never` | `Real` | Never |
| `cmpfunc_notequal` | `Real` | Not Equal |

### (sin clase)

| Constante | Tipo | Descripción |
|---|---|---|
| `$$implicit_argument$$` | `Undefined` |  |
| `GM_build_date` | `Real` | This constant holds the date and time on which the executable being run was built by GameMaker. |
| `GM_build_type` | `String` | compile time constant of current build type either "exe" (for create executable) or "run" (for a run) |
| `GM_is_sandboxed` | `Bool` | compile time constant of whether game is sandboxed or not (true - sandbox is on, false - sandbox is off) |
| `GM_project_filename` | `String` | full path and filename of the YYP project |
| `GM_runtime_type` | `String` | This built-in constant holds the type of the runtime: "gms2" for the current runtime or "gmrt" for the new runtime. |
| `GM_runtime_version` | `String` | This constant hold the runtime version number as defined in the Runtime Feeds Preferences as the runtime being used to build the project. |
| `GM_version` | `String` | This constant hold the version number as defined in the Game Options for each target platform. |
| `NaN` | `Real` | NaN stands for "not a number", and is a constant that can be returned when the compiler cannot evaluate the results of an operation as a number. |
| `_GMFILE_` | `String` | compile time constant that returns the current filename |
| `_GMFUNCTION_` | `String` | compile time constant that returns the current function name |
| `_GMLINE_` | `Real` | compile time constant that returns the current line number |
| `achievement_achievement_info` ⚠️obsoleta | `Real` |  |
| `achievement_friends_info` ⚠️obsoleta | `Real` |  |
| `achievement_leaderboard_info` ⚠️obsoleta | `Real` |  |
| `achievement_our_info` ⚠️obsoleta | `Real` |  |
| `achievement_pic_loaded` ⚠️obsoleta | `Real` |  |
| `achievement_show_achievement` ⚠️obsoleta | `Real` |  |
| `achievement_show_bank` ⚠️obsoleta | `Real` |  |
| `achievement_show_friend_picker` ⚠️obsoleta | `Real` |  |
| `achievement_show_leaderboard` ⚠️obsoleta | `Real` |  |
| `achievement_show_profile` ⚠️obsoleta | `Real` |  |
| `achievement_show_purchase_prompt` ⚠️obsoleta | `Real` |  |
| `achievement_show_ui` ⚠️obsoleta | `Real` |  |
| `audio_bus_main` | `Struct.AudioBus` | The main audio bus |
| `audio_new_system` ⚠️obsoleta | `Real` |  |
| `audio_old_system` ⚠️obsoleta | `Real` |  |
| `display_landscape` | `Real` | The device is being held horizontally i.e.: The longest edge is from left to right, and the menu button is on the right. |
| `display_landscape_flipped` | `Real` | As above, only now the menu button is on the left. |
| `display_portrait` | `Real` | The device is being held vertically i.e.: The longest edge is from top to bottom, and the menu button is at the bottom. |
| `display_portrait_flipped` | `Real` | As above, only now the menu button is at the top. |
| `false` | `Bool` | 0 (although any value less than 1 will also evaluate as false) |
| `global` | `Real` | The global keyword |
| `iap_available` | `Real` |  |
| `iap_canceled` | `Real` |  |
| `iap_ev_consume` | `Real` |  |
| `iap_ev_product` | `Real` |  |
| `iap_ev_purchase` | `Real` |  |
| `iap_ev_restore` | `Real` |  |
| `iap_ev_storeload` | `Real` |  |
| `iap_failed` | `Real` |  |
| `iap_purchased` | `Real` |  |
| `iap_refunded` | `Real` |  |
| `iap_status_available` | `Real` |  |
| `iap_status_loading` | `Real` |  |
| `iap_status_processing` | `Real` |  |
| `iap_status_restoring` | `Real` |  |
| `iap_status_unavailable` | `Real` |  |
| `iap_status_uninitialised` | `Real` |  |
| `iap_storeload_failed` | `Real` |  |
| `iap_storeload_ok` | `Real` |  |
| `iap_unavailable` | `Real` |  |
| `infinity` | `Real` | The constant infinity refers to a number that is considered infinite, such as the result you would get when dividing any floating point value by zero. |
| `leaderboard_type_number` ⚠️obsoleta | `Real` |  |
| `leaderboard_type_time_mins_secs` ⚠️obsoleta | `Real` |  |
| `mip_markedonly` | `Real` | Mipmapping is enabled for textures that have it enabled in the Texture Group options (default). |
| `mip_off` | `Real` | Mipmapping is disabled. |
| `mip_on` | `Real` | Mipmapping for all textures is enabled. |
| `noone` | `Id.Instance` | The noone keyword |
| `of_challenge_lose` ⚠️obsoleta | `Real` |  |
| `of_challenge_tie` ⚠️obsoleta | `Real` |  |
| `of_challenge_win` ⚠️obsoleta | `Real` |  |
| `os_permission_denied` | `Real` | This indicates that the permission has not been granted |
| `os_permission_denied_dont_request` | `Real` | This indicates that the permission has either been blocked by the phone settings, or that the user has previously denied the request and selected "Don't ask again". |
| `os_permission_granted` | `Real` | This indicates that the permission has been granted |
| `other` | `Id.Instance` | The other keyword |
| `pi` | `Real` | 3.141592653589793280... (the exact value will depend on various factors like the platform being targeted) |
| `pointer_invalid` | `Pointer` | This constant means that the value is not a valid pointer |
| `pointer_null` | `Pointer` | This constant indicates that the pointer is not pointing to anything meaningful (the same as NULL in C++ or null in C#). This value is falsy. |
| `rollback_chat_message` | `Real` | Fired when you receive a chat message, including those sent by the local player (in rollback_event_param) message, from and to |
| `rollback_connect_error` | `Real` | Fired when you fail to connect to the backend |
| `rollback_connect_info` | `Real` | Fired when you get info of where players should connect (in rollback_event_param) share_url |
| `rollback_connected_to_peer` | `Real` | Fired when the (in rollback_event_param) player_id is connected |
| `rollback_connection_rejected` | `Real` | Fired when connection attempt was rejected. The error can be caused by invalid token, mismatch in client versions, mismatch in protocol versions. Multiplayer session is closed auto |
| `rollback_disconnected_from_peer` | `Real` | Fired when the (in rollback_event_param) player_id is disconnected |
| `rollback_end_game` | `Real` | Fired when server wants clients to stop the game. Usually this event means that clients are in inconsistent state. Multiplayer session is closed automatically before event is fired |
| `rollback_game_full` | `Real` | Fired when the game you're trying to join is already full |
| `rollback_game_info` | `Real` | Fired when you receive back info about the game (in rollback_event_param) player_id and num_players |
| `rollback_game_interrupted` | `Real` | Fired when the game is interrupted by a (in rollback_event_param) player_id |
| `rollback_game_resumed` | `Real` | Fired when the game resumes after being interrupted by (in rollback_event_param) player_id |
| `rollback_high_latency` | `Real` | Fired when the latency to the server is too high and it's impossible to run the game. Multiplayer session is closed automatically before event is fired |
| `rollback_player_prefs` | `Real` | Fired when you receive new preferences set by any of the players in the game, including those set by the local player (in rollback_event_param) preferences, and player_id |
| `rollback_protocol_rejected` | `Real` | Fired when connection attempt was rejected. The error means that client uses obsolete version of the protocol. Before this event is fired GM will show an error message in the UI. M |
| `rollback_synchronized_with_peer` | `Real` | Fired when the (in rollback_event_param) player_id is done synchonizing |
| `rollback_synchronizing_with_peer` | `Real` | Fired when the (in rollback_event_param) player_id is synchonizing |
| `self` | `Id.Instance` | The self keyword |
| `seqinterpolation_assign` | `Real` | Don't use interpolation for this track |
| `seqinterpolation_lerp` | `Real` | Use linear interpolation for this track |
| `sprite_add_ext_error_cancelled` | `Real` | This constant indicates that the request was cancelled while it was in progress. |
| `sprite_add_ext_error_decompressfailed` | `Real` | This constant indicates that image decompression failed (which could be due to e.g. a corrupted file or unsupported image format). |
| `sprite_add_ext_error_loadfailed` | `Real` | This constant indicates that a file loading operation failed. |
| `sprite_add_ext_error_setupfailed` | `Real` | Indicates that, even though all data was loaded and decompressed, sprite resource creation itself failed. |
| `sprite_add_ext_error_spritenotfound` | `Real` | This constant indicates that a sprite was removed somehow partway through the loading process. |
| `sprite_add_ext_error_unknown` | `Real` | This is a generic error code when none of the others apply (the HTML5 runner only returns this constant in case of failure). |
| `tf_anisotropic` | `Real` | This means that anisotropic filtering is enabled, which greatly improves texture transition quality and can reduce the blurring visible with other filtering modes, but it has the h |
| `tf_linear` | `Real` | This means that blending between mipmap levels is enabled (this is also known as trilinear filtering), which smooths the texture transitions, but it will give a minor hit to perfor |
| `tf_point` | `Real` | This means that blending between mipmap levels is disabled, which can cause visible texture transitions, but gives the best performance. |
| `timezone_local` | `Real` | use the local time zone as set by the system |
| `timezone_utc` | `Real` | use Coordinated Universal Time |
| `true` | `Bool` | 1 (although any value equal to or greater than 1 will evaluate as true) |
| `undefined` | `Undefined` | The special constant undefined |

## Enumeraciones


### `AudioEffectType`

| Miembro | Valor | Descripción |
|---|---|---|
| `Bitcrusher` | 0 | Distorts sound by reducing bandwidth. |
| `Delay` | 1 | A delay/echo effect. |
| `Gain` | 2 | A smoothed gain scalar effect. |
| `HPF2` | 3 | A high-pass filter effect. |
| `LPF2` | 4 | A low-pass filter effect. |
| `Reverb1` | 5 | A reverberation effect. |
| `Tremolo` | 6 | A gain modulator effect. |
| `PeakEQ` | 7 | A peak EQ filter effect. |
| `HiShelf` | 8 | A high-shelf filter effect |
| `LoShelf` | 9 | A low-shelf filter effect. |
| `EQ` | 10 | A parametric EQ effect. |
| `Compressor` | 11 | A dynamic range compressor effect. |

### `AudioLFOType`

| Miembro | Valor | Descripción |
|---|---|---|
| `InvSawtooth` | 0 | An inverted sawtooth waveshape. |
| `Sawtooth` | 1 | A sawtooth waveshape. |
| `Sine` | 2 | A sine waveshape. |
| `Square` | 3 | A square waveshape. |
| `Triangle` | 4 | A triangle waveshape. |

### `colspace`

| Miembro | Valor | Descripción |
|---|---|---|
| `room` | 0 | Room Space |
| `ui_view` | 1 | View space UI Layers |
| `ui_display` | 2 | Display space UI Layers |
| `colspace_all` | 3 | All collision spaces |

### `flexpanel_align`

| Miembro | Valor | Descripción |
|---|---|---|
| `auto` | 0 | Auto align |
| `flex_start` | 1 | flex_start |
| `center` | 2 | center |
| `flex_end` | 3 | flex_end |
| `stretch` | 4 | stretch |
| `baseline` | 5 | baseline |
| `space_between` | 6 | space_between |
| `space_around` | 7 | space_around |
| `space_evenly` | 8 | space_evenly |

### `flexpanel_direction`

| Miembro | Valor | Descripción |
|---|---|---|
| `inherit` | 0 | Inherit layout direction from parent |
| `LTR` | 1 | Layout calculated from left to right |
| `RTL` | 2 | Layout calculated from right to left |

### `flexpanel_display`

| Miembro | Valor | Descripción |
|---|---|---|
| `flex` | 0 | Normal display |
| `none` | 1 | No display |

### `flexpanel_edge`

| Miembro | Valor | Descripción |
|---|---|---|
| `left` | 0 | the left edge |
| `top` | 1 | the top edge |
| `right` | 2 | The right edge |
| `bottom` | 3 | The bottom edge |
| `start` | 4 | Start of the node |
| `_end` | 5 | End of the node |
| `horizontal` | 6 | Horizontal edges |
| `vertical` | 7 | Vertical edges |
| `all_edges` | 8 | All edges |

### `flexpanel_flex_direction`

| Miembro | Valor | Descripción |
|---|---|---|
| `column` | 0 | Vertical layout |
| `column_reverse` | 1 | Reverse vertical layout |
| `row` | 2 | Horizontal layout |
| `row_reverse` | 3 | Reverse horizontal layout |

### `flexpanel_gutter`

| Miembro | Valor | Descripción |
|---|---|---|
| `column` | 0 | gapColumn |
| `row` | 1 | gapRow |
| `all_gutters` | 2 | gap |

### `flexpanel_justify`

| Miembro | Valor | Descripción |
|---|---|---|
| `start` | 0 | flex_start |
| `center` | 1 | center |
| `flex_end` | 2 | flex_end |
| `space_between` | 3 | space_between |
| `space_around` | 4 | space_around |
| `space_evenly` | 5 | space_evenly |

### `flexpanel_position_type`

| Miembro | Valor | Descripción |
|---|---|---|
| `static` | 0 | Static position type |
| `relative` | 1 | Relative position type |
| `absolute` | 2 | Absolute position type |

### `flexpanel_unit`

| Miembro | Valor | Descripción |
|---|---|---|
| `point` | 1 | Number of pixels. |
| `percent` | 2 | A Percentage value. |
| `auto` | 3 | auto |

### `flexpanel_wrap`

| Miembro | Valor | Descripción |
|---|---|---|
| `no_wrap` | 0 | Disable wrapping |
| `wrap` | 1 | Enable wrapping |
| `reverse` | 2 | Enable reverse wrapping |
