###############################################################################
#    tmux common profile
#      This tmux configuration profile is intended to correspond to Byobu's
#      traditional GNU Screen profile
#
#    Copyright (C) 2011 Dustin Kirkland
#
#    Authors: Dustin Kirkland <kirkland@byobu.co>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

# Initialize environment, clean up
set-environment -g BYOBU_BACKEND tmux
new-window -d byobu-janitor
set -s escape-time 0

# Change to Screen's ctrl-a escape sequence
source /usr/share/doc/tmux/examples/screen-keys.conf
# On Archlinux, this file is not under the same directory
source /usr/share/tmux/screen-keys.conf

# Add F12 to the prefix list
set -g prefix ^A,F12

# Byobu's Keybindings
source $BYOBU_PREFIX/share/byobu/keybindings/f-keys.tmux

set-option -g set-titles on
set-option -g set-titles-string '#(whoami)@#H - byobu (#S)'
set-option -g pane-active-border-bg $BYOBU_ACCENT
set-option -g pane-active-border-fg $BYOBU_ACCENT
set-option -g pane-border-fg $BYOBU_LIGHT
set-option -g history-limit 10000
set-option -g display-panes-time 150
set-option -g display-panes-colour $BYOBU_ACCENT
set-option -g display-panes-active-colour $BYOBU_HIGHLIGHT
set-option -g clock-mode-colour $BYOBU_ACCENT
set-option -g clock-mode-style 24
set-option -g mode-keys vi

set-window-option -g automatic-rename off
set-window-option -g aggressive-resize on
set-window-option -g monitor-activity on

# Cannot use:
#  - screen-bce, screen-256color-bce: tmux does not support bce
#  - screen-256color: vim broken without -bce
set -g default-terminal "screen"

# The following helps with Shift-PageUp/Shift-PageDown
set -g terminal-overrides 'xterm*:smcup@:rmcup@'

# Must set default-command to $SHELL, in order to not source ~/.profile
# BUG: Should *not* hardcode /bin/bash here
set -g default-command $SHELL

# Allow local overrides
source $BYOBU_CONFIG_DIR/.tmux.conf

set-option -g renumber-windows on

source ~/.vim/bundle/powerline/powerline/bindings/tmux/powerline.conf
