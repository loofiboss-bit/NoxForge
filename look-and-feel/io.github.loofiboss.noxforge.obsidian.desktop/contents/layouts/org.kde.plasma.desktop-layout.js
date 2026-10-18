var panel = new Panel;
panel.location = "bottom";
panel.height = 44;
panel.floating = true;
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
    desktops[index].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desktops[index].writeConfig("Image", "NoxForge-Obsidian");
}
