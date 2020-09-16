if [ $# -eq 1 ]
  then
    git add -A
	git add -u
	git commit -m $1
	git push
else
	git add -A
	git add -u
	git commit -m "No message specified"
	git push
fi