#!/bin/sh
#
# LightDM wrapper to run around X sessions.

echo "Running X session wrapper"

# Load profile
for file in "/etc/profile" "$HOME/.profile" "/etc/xprofile" "$HOME/.xprofile"; do
    if [ -f "$file" ]; then
        echo "Loading profile from $file";
        . "$file"
    fi
done

# Load resources
for file in "/etc/X11/Xresources" "$HOME/.Xresources"; do
    if [ -f "$file" ]; then
        echo "Loading resource: $file"
        xrdb -merge "$file"
    fi
done

# Load keymaps
for file in "/etc/X11/Xkbmap" "$HOME/.Xkbmap"; do
    if [ -f "$file" ]; then
        echo "Loading keymap: $file"
        setxkbmap `cat "$file"`
        XKB_IN_USE=yes
    fi
done

# Load xmodmap if not using XKB
if [ -z "$XKB_IN_USE" ]; then
    for file in "/etc/X11/Xmodmap" "$HOME/.Xmodmap"; do
        if [ -f "$file" ]; then
           echo "Loading modmap: $file"
           xmodmap "$file"
        fi
    done
fi

unset XKB_IN_USE

# Run all system xinitrc shell scripts
xinitdir="/etc/X11/xinit/xinitrc.d"
if [ -d "$xinitdir" ]; then
    for script in $xinitdir/*; do
        echo "Loading xinit script $script"
        if [ -x "$script" -a ! -d "$script" ]; then
            . "$script"
        fi
    done
fi

# Run user xsession shell script
script="$HOME/.xsession"
if [ -x "$script" -a ! -d "$script" ]; then
    echo "Loading xsession script $script"
    . "$script"
fi

if [[ " ${@[@]} " =~ " gnome|xfce|openbox " && "$(which light-locker)" ]]; then
    # Ensure that Light Locker starts before session manager.
    /usr/bin/light-locker &
    sleep 3
fi

if ! [[ " ${@[@]} " =~ " plasma|lxqt " ]]; then
    # Fix ugly styles for Qt applications when running under GTK-based desktops and Qt 5.7+
    export QT_QPA_PLATFORMTHEME='qt5ct'
    export QT_STYLE_OVERRIDE=''
fi

echo "X session wrapper complete, running session $*"

exec "$@"