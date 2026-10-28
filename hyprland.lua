-- Ono-Sendai: red border fading into deck black, blurred translucent surfaces.
local active_border_color = { colors = { "rgba(e8261bee)", "rgba(4d0d09ee)" }, angle = 45 }
local inactive_border_color = "rgba(24161599)"

hl.config({
  general = {
    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  },

  decoration = {
    blur = {
      enabled = true,
      size = 6,
      passes = 3,
      noise = 0.02,
      contrast = 1.0,
      brightness = 0.85,
      vibrancy = 0.1,
      popups = true,
    },
  },
})

-- Blur behind the translucent shell surfaces (bar, dock, menus, prompts, notifications).
hl.layer_rule({
  match = { namespace = "^(omarchy-bar|omarchy-dock|omarchy-dock-apps|omarchy-menu|omarchy-polkit|omarchy-image-selector|omarchy-emojis|omarchy-clipboard|omarchy-keyboard-panel|omarchy-notifications|omarchy-osd|omarchy-reminders|omarchy-network-qr)$" },
  blur = true,
  ignore_alpha = 0.3,
})

-- Let the wallpaper show through the windows Omarchy makes see-through, more
-- so when unfocused, and terminals most of all. Keeping the transparent-window
-- tag lets the window-opaque toggle still turn them solid.
o.transparent_window({ tag = "transparent-window" }, "0.94 0.86")
o.transparent_window({ tag = "terminal" }, "0.88 0.80")
