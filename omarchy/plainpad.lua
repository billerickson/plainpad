-- Omarchy 4 / Hyprland Lua configuration. Static rules apply when opened;
-- the normal Super+T binding can still toggle floating and tiling.
o.window("^local[.]plainpad[.]Plainpad$", {
  float = true,
  center = true,
  size = { 820, 460 },
})
