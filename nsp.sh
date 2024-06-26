#!/bin/sh
# vim: set tabstop=8 shiftwidth=8 noexpandtab:

SELF="$0"

TSV_FILE=nsp.tsv
AWK_FILE=nsp.awk

get_data() {
	sed '1,/^#EOF$/d' < "$SELF" | tar xzf - -O "$1"
}

if [ -z "$PAGER" ]; then
	if command -v less >/dev/null; then
		PAGER="less"
	else
		PAGER="cat"
	fi
fi

list_books() {
	get_data $TSV_FILE | awk -v cmd=list "$(get_data $AWK_FILE)"
}

rand_verse() {
	# Get the total number of lines (verses) in the dataset
	total_verses=$(get_data $TSV_FILE | wc -l)

    # Check if total_verses is greater than 0
    if [ "$total_verses" -gt 0 ]; then
	    # Generate a random line number within the total range
	    random_line_number=$((RANDOM % total_verses + 1))

	# Fetch the random verse using awk
	random_verse=$(get_data $TSV_FILE | awk -F'\t' -v line_number="$random_line_number" 'NR == line_number {
	printf "%s\n%s:%s\t%s\n", $1, $4, $5, $6
}')

	# Apply text wrapping if not disabled
	if [ -z "$KJV_NOLINEWRAP" ]; then
		echo "$random_verse" | fold -w 72 -s | sed -e '3,$s/^/        /' | ${PAGER}
	else
		echo "$random_verse" | ${PAGER}
	fi
else
	echo "No verses found in the dataset."
	fi
}

show_help() {
	exec >&2
	echo "usage: $(basename "$0") [flags] [reference...]"
	echo
	echo "  -l      list books"
	echo "  -r      random verse"
	echo "  -W      no line wrap"
	echo "  -h      show help"
	echo
	echo "  Reference types:"
	echo "      <Book>"
	echo "          Individual book"
	echo "      <Book>:<Chapter>"
	echo "          Individual chapter of a book"
	echo "      <Book>:<Chapter>:<Verse>[,<Verse>]..."
	echo "          Individual verse(s) of a specific chapter of a book"
	echo "      <Book>:<Chapter>-<Chapter>"
	echo "          Range of chapters in a book"
	echo "      <Book>:<Chapter>:<Verse>-<Verse>"
	echo "          Range of verses in a book chapter"
	echo "      <Book>:<Chapter>:<Verse>-<Chapter>:<Verse>"
	echo "          Range of chapters and verses in a book"
	echo
	echo "      /<Search>"
	echo "          All verses that match a pattern"
	echo "      <Book>/<Search>"
	echo "          All verses in a book that match a pattern"
	echo "      <Book>:<Chapter>/<Search>"
	echo "          All verses in a chapter of a book that match a pattern"
	echo 
	echo "  Interactive mode commands:"
	echo "      list"
	echo "	        list books"
	echo "      help"
	echo "	        show help"
}

while [ $# -gt 0 ]; do
	isFlag=0
	firstChar="${1%"${1#?}"}"
	if [ "$firstChar" = "-" ]; then
		isFlag=1
	fi

	if [ "$1" = "--" ]; then
		shift
		break
	elif [ "$1" = "-l" ]; then
		# List all book names with their abbreviations
		list_books
		exit
	elif [ "$1" = "-r" ]; then
		# Return random verse
		rand_verse | cat
		exit
	elif [ "$1" = "-W" ]; then
		export KJV_NOLINEWRAP=1
		shift
	elif [ "$1" = "-h" ] || [ "$isFlag" -eq 1 ]; then
		show_help
		exit 2
	else
		break
	fi
done

cols=$(tput cols 2>/dev/null)
if [ $? -eq 0 ]; then
	export KJV_MAX_WIDTH="$cols"
fi

if [ $# -eq 0 ]; then
	if [ ! -t 0 ]; then
		show_help
	fi

	# Interactive mode
	while true; do
		printf "nsp> "
		if ! read -r ref; then
			break
		fi


		case "$ref" in 
			list)
				list_books
				;;
			help)
				show_help
				;;
			*)
				get_data $TSV_FILE | awk -v cmd=ref -v ref="$ref" "$(get_data $AWK_FILE)" | ${PAGER}
				;;
		esac
	done
	exit 0
fi

get_data $TSV_FILE | awk -v cmd=ref -v ref="$*" "$(get_data $AWK_FILE)" | ${PAGER}
