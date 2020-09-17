module.exports = {
  apps : [{
	name: "Utilibot",
    script: 'python3.8 main.py',
    watch: '.',
	ignore_watch : ["/home/pi/cogs/__pycache__/*"]
  }],
};
