if [ $# -gt 0 ]
  then
    git add -A
	git add -u
	git commit -m $1
	git push
else
	git add -A
	git add -u
	git commit -m "$*"
	git push
fi