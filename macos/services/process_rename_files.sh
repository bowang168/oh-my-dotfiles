#!/bin/bash
# Process and Rename Files - Finder Quick Action
# Renames files/folders, converts images to JPEG, resizes, and applies naming conventions.

gcd() {
    local a=$1 b=$2
    while (( b != 0 )); do
        local t=$b
        b=$((a % b))
        a=$t
    done
    echo $a
}

for f in "$@"; do
    [ -e "$f" ] || continue

    dir=$(dirname "$f")
    base=$(basename "$f")
    is_image=false
    is_dir=false

    [ -d "$f" ] && is_dir=true

    # Step 1: Get creation date
    creation_date=$(stat -f "%SB" -t "%Y-%m-%d" "$f")

    # Step 2: Replace spaces with underscores, lowercase extension
    if [ "$is_dir" = true ]; then
        new_base="${base// /_}"
    else
        name="${base%.*}"
        ext="${base##*.}"
        if [ "$name" = "$base" ]; then
            new_base="${base// /_}"
        else
            ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
            name="${name// /_}"
            new_base="${name}.${ext_lower}"
        fi
    fi

    if [ "$base" != "$new_base" ]; then
        mv "$f" "$dir/$new_base"
        f="$dir/$new_base"
        base="$new_base"
    fi

    # Determine if image by extension
    if [ "$is_dir" = false ]; then
        ext_lower=$(echo "${base##*.}" | tr '[:upper:]' '[:lower:]')
        case "$ext_lower" in
            jpg|jpeg|png|gif|bmp|tiff|tif|webp|heic|heif)
                is_image=true
                ;;
        esac
    fi

    # Step 3: Convert non-JPEG images to JPEG
    if [ "$is_image" = true ]; then
        case "$ext_lower" in
            jpg|jpeg)
                ;;
            *)
                name="${base%.*}"
                sips -s format jpeg "$f" --out "$dir/${name}.jpg" >/dev/null 2>&1
                if [ -f "$dir/${name}.jpg" ] && [ -s "$dir/${name}.jpg" ]; then
                    rm "$f"
                    f="$dir/${name}.jpg"
                    base="${name}.jpg"
                    ext_lower="jpg"
                fi
                ;;
        esac
    fi

    # Step 4: Check/add YYYY-MM-DD_ prefix
    if [ "$is_dir" = true ]; then
        name="$base"
    else
        name="${base%.*}"
        ext="${base##*.}"
    fi

    if ! echo "$name" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}_'; then
        if [ "$is_dir" = true ]; then
            new_base="${creation_date}_${name}"
        else
            new_base="${creation_date}_${name}.${ext}"
        fi
        mv "$f" "$dir/$new_base"
        f="$dir/$new_base"
        base="$new_base"
        if [ "$is_dir" = true ]; then
            name="$base"
        else
            name="${base%.*}"
        fi
    fi

    # Steps 5 & 6: Image-specific processing
    if [ "$is_image" = true ]; then
        width=$(sips -g pixelWidth "$f" 2>/dev/null | tail -1 | awk '{print $2}')
        height=$(sips -g pixelHeight "$f" 2>/dev/null | tail -1 | awk '{print $2}')

        if [ -n "$width" ] && [ -n "$height" ] && [ "$width" -gt 0 ] 2>/dev/null && [ "$height" -gt 0 ] 2>/dev/null; then
            name="${base%.*}"
            ext="${base##*.}"

            # 5.1: Determine orientation and modify filename
            if (( width > height )); then
                orientation="landscape"
                marker="_h_"
            else
                orientation="portrait"
                marker="_v_"
            fi

            # Only apply if _h_ or _v_ not already in name
            if [[ "$name" != *_h_* ]] && [[ "$name" != *_v_* ]]; then
                new_name=$(echo "$name" | sed "s/_/${marker}/")
                if [ "$name" != "$new_name" ]; then
                    new_base="${new_name}.${ext}"
                    mv "$f" "$dir/$new_base"
                    f="$dir/$new_base"
                    base="$new_base"
                    name="$new_name"
                fi
            fi

            # 5.2: Resize landscape images
            if [ "$orientation" = "landscape" ]; then
                if (( width > 1600 )); then
                    sips --resampleWidth 1600 "$f" >/dev/null 2>&1
                elif (( width > 1200 )); then
                    sips --resampleWidth 1200 "$f" >/dev/null 2>&1
                fi
            # 5.3: Resize portrait images
            else
                if (( width > 1200 )); then
                    sips --resampleWidth 1200 "$f" >/dev/null 2>&1
                elif (( width > 900 )); then
                    sips --resampleWidth 900 "$f" >/dev/null 2>&1
                fi
            fi

            # Re-read dimensions after resize
            width=$(sips -g pixelWidth "$f" 2>/dev/null | tail -1 | awk '{print $2}')
            height=$(sips -g pixelHeight "$f" 2>/dev/null | tail -1 | awk '{print $2}')

            # Step 6: Check ratio and add suffix
            if [ -n "$width" ] && [ -n "$height" ] && [ "$width" -gt 0 ] 2>/dev/null && [ "$height" -gt 0 ] 2>/dev/null; then
                g=$(gcd "$width" "$height")
                rw=$((width / g))
                rh=$((height / g))

                name="${base%.*}"
                ext="${base##*.}"

                if [ "$orientation" = "portrait" ] && [ "$rw" -eq 3 ] && [ "$rh" -eq 4 ]; then
                    if [[ "$name" != *_34 ]]; then
                        new_base="${name}_34.${ext}"
                        mv "$f" "$dir/$new_base"
                        f="$dir/$new_base"
                    fi
                elif [ "$orientation" = "landscape" ] && [ "$rw" -eq 4 ] && [ "$rh" -eq 3 ]; then
                    if [[ "$name" != *_43 ]]; then
                        new_base="${name}_43.${ext}"
                        mv "$f" "$dir/$new_base"
                        f="$dir/$new_base"
                    fi
                fi
            fi
        fi
    fi
done

osascript -e 'display notification "Files processed successfully" with title "Process and Rename Files"'
