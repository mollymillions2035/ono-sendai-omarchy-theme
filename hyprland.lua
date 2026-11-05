-- Ono-Sendai: red border fading into deck black. Transparency and blur are left
-- to Omarchy's own settings.
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
})
