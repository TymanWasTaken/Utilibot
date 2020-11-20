if [ $# -gt 0 ]
  then
    git add -A
	git commit -m "$*"
	git push
else
	git add -A
	git commit -m "No message specified"
	git push
fi
