git add .
if [ $# -gt 0 ]
  then
	git commit -am "$*"
else
	git commit -am "No message specified"
fi
git push