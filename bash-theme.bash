# Applies the current Omarchy theme's bash.theme to an interactive bash:
# the starship prompt, readline's completion prefix and active region, and fzf.
# Source it once from ~/.bashrc, after Omarchy's rc (see README.md):
#
#   source ~/Work/ono-sendai-omarchy-theme/bash-theme.bash
#
# bash.theme is parsed, never sourced, so a theme can only supply colours:
# keys outside the lists below and anything that isn't a 6-digit hex colour
# are skipped. A theme without a bash.theme leaves bash on Omarchy's defaults.
# New shells pick up a theme switch; open ones keep their colours.

[[ $- == *i* ]] || return 0

__omarchy_bash_theme() {
  local theme=${XDG_STATE_HOME:-$HOME/.local/state}/omarchy/current/theme/bash.theme
  [[ -r $theme ]] || return 0

  local key fg rest arg sgr fzf_attrs bg palette="" fzf=""
  local hex='^[0-9a-fA-F]{6}$'
  local -a args

  # "rrggbb" -> "r;g;b"
  rgb() { printf '%d;%d;%d' "0x${1:0:2}" "0x${1:2:2}" "0x${1:4:2}"; }

  while read -r key fg rest; do
    [[ -z $key || $key == \#* ]] && continue
    [[ $fg =~ $hex ]] || continue

    read -ra args <<<"$rest"
    sgr="" fzf_attrs="" bg=""
    for arg in "${args[@]}"; do
      case $arg in
        --bold) sgr+="1;" fzf_attrs+=":bold" ;;
        --underline) sgr+="4;" fzf_attrs+=":underline" ;;
        --italics) sgr+="3;" fzf_attrs+=":italic" ;;
        --background=*) [[ ${arg#*=} =~ $hex ]] && bg=${arg#*=} ;;
      esac
    done
    sgr+="38;2;$(rgb "$fg")"
    [[ -n $bg ]] && sgr+=";48;2;$(rgb "$bg")"

    case $key in
      starship_color_black | starship_color_red | starship_color_green | \
        starship_color_yellow | starship_color_blue | starship_color_purple | \
        starship_color_cyan | starship_color_white | starship_color_bright-*)
        palette+="${key#starship_color_} = \"#$fg\""$'\n'
        ;;
      bash_color_completion_prefix)
        LS_COLORS="${LS_COLORS:+$LS_COLORS:}*readline-colored-completion-prefix=$sgr"
        export LS_COLORS
        bind 'set colored-completion-prefix on'
        ;;
      bash_color_region)
        bind "set active-region-start-color \"\\e[${sgr}m\""
        bind 'set active-region-end-color "\e[0m"'
        ;;
      fzf_color_fg | fzf_color_bg | fzf_color_hl | fzf_color_fg+ | fzf_color_bg+ | \
        fzf_color_hl+ | fzf_color_query | fzf_color_prompt | fzf_color_pointer | \
        fzf_color_marker | fzf_color_spinner | fzf_color_info | fzf_color_header | \
        fzf_color_border | fzf_color_separator | fzf_color_scrollbar | fzf_color_gutter)
        fzf+="${fzf:+,}${key#fzf_color_}:#$fg$fzf_attrs"
        ;;
    esac
  done <"$theme"
  unset -f rgb

  [[ -n $fzf ]] && export FZF_DEFAULT_OPTS="${FZF_DEFAULT_OPTS:+$FZF_DEFAULT_OPTS }--color=$fzf"

  # Starship reads one config file, so write the user's own with the theme's
  # palette added. Palette names override starship's named colours, so the
  # prompt's layout stays whatever ~/.config/starship.toml says. A config that
  # already picks its own palette is left alone.
  local base=${XDG_CONFIG_HOME:-$HOME/.config}/starship.toml
  local out=${XDG_CACHE_HOME:-$HOME/.cache}/omarchy/starship-bash-theme.toml
  if [[ -n $palette && -r $base ]] && ! grep -qE '^[[:space:]]*palette[[:space:]]*=' "$base"; then
    if [[ ! -f $out || $theme -nt $out || $base -nt $out ]]; then
      mkdir -p "${out%/*}"
      local tmp
      tmp=$(mktemp "$out.XXXXXX") &&
        { printf 'palette = "omarchy_bash_theme"\n\n'; cat "$base"
          printf '\n[palettes.omarchy_bash_theme]\n%s' "$palette"; } >"$tmp" &&
        mv -f "$tmp" "$out"
    fi
    [[ -f $out ]] && export STARSHIP_CONFIG=$out
  fi
}

__omarchy_bash_theme
unset -f __omarchy_bash_theme
