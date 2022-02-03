; Based on Sandbert values

hurtbox_spr = asset_get("ex_guy_hurt_box");
crouchbox_spr = asset_get("ex_guy_crouch_box");
air_hurtbox_spr = -1;
hitstun_hurtbox_spr = -1;

char_height = 52;
idle_anim_speed = .1;
crouch_anim_speed = .1;
walk_anim_speed = .125;
dash_anim_speed = .2;
pratfall_anim_speed = .25;

walk_speed = 3.25;
walk_accel = 0.2;
walk_turn_time = 6;
initial_dash_time = 14;
initial_dash_speed = 8;
dash_speed = 7.5;
dash_turn_time = 10;
dash_turn_accel = 1.5;
dash_stop_time = 4;
dash_stop_percent = .35;
ground_friction = .5;
moonwalk_accel = 1.4;

jump_start_time = 5;
jump_speed = 13;
short_hop_speed = 8;
djump_speed = 12;
leave_ground_max = 7;
max_jump_hsp = 7;
air_max_speed = 7;
jump_change = 3;
air_accel = .3;
prat_fall_accel = .85;
air_friction = .02;
max_djumps = 1;
double_jump_time = 32;
walljump_hsp = 7;
walljump_vsp = 11;
walljump_time = 32;
max_fall = 13;
fast_fall = 16;
gravity_speed = .65;
hitstun_grav = .5;
knockback_adj = 1.0;

land_time = 4;
prat_land_time = 3;
wave_land_time = 8;
wave_land_adj = 1.35;
wave_friction = .04;

crouch_startup_frames = 1;
crouch_active_frames = 1;
crouch_recovery_frames = 1;

dodge_startup_frames = 1;
dodge_active_frames = 1;
dodge_recovery_frames = 3;

tech_active_frames = 3;
tech_recovery_frames = 1;

techroll_startup_frames = 2
techroll_active_frames = 2;
techroll_recovery_frames = 2;
techroll_speed = 10;

air_dodge_startup_frames = 1;
air_dodge_active_frames = 2;
air_dodge_recovery_frames = 3;
air_dodge_speed = 7.5;

roll_forward_startup_frames = 2;
roll_forward_active_frames = 4;
roll_forward_recovery_frames = 2;
roll_back_startup_frames = 2;
roll_back_active_frames = 4;
roll_back_recovery_frames = 2;
roll_forward_max = 9; //roll speed
roll_backward_max = 9;

land_sound = asset_get("sfx_land_med");
landing_lag_sound = asset_get("sfx_land");
waveland_sound = asset_get("sfx_waveland_zet");
jump_sound = asset_get("sfx_jumpground");
djump_sound = asset_get("sfx_jumpair");
air_dodge_sound = asset_get("sfx_quick_dodge");

bubble_x = 0;
bubble_y = 8;
