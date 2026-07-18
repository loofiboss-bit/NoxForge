var panel = new Panel;
panel.location = "bottom";
panel.height = 40;
panel.addWidget("org.kde.plasma.kickoff");
panel.addWidget("org.kde.plasma.pager");
panel.addWidget("org.kde.plasma.icontasks");
panel.addWidget("org.kde.plasma.marginsseparator");
panel.addWidget("org.kde.plasma.systemtray");
panel.addWidget("org.kde.plasma.digitalclock");
panel.addWidget("org.kde.plasma.showdesktop");

var desktops = desktopsForActivity(currentActivity());
for (var index = 0; index < desktops.length; index++) {
    desktops[index].wallpaperPlugin = "org.kde.image";
}
