---
title: "Wireless Ping Spikes on Windows 10"
excerpt_separator: "<!--more-->"
categories:
  - Blog
---

Windows 10 has a problem with wireless ping spikes, this is what I know about
it and what I've been able to figure about how to deal with it. As I write this, I'm not sure if this is a bug report or a complaint or just
some documentation to pass on what I have learned. Maybe all of the above.

The symptoms of the problem are fairly accurately captured by the following
screenshot, but basically what happens is every now and then my wireless
network connection starts stuttering every 4-5 seconds.  Packets aren't
usually lost, just the network adapter seems to hang for a second then resume
normal operation for moment, then stutter again.

<video width="100%" autoplay="autoplay" loop="loop">
    <source src="/assets/images/ping-spike.webm" type="video/webm">
</video>

<!--more-->

Although the problem is intermittent, once the computer is experiencing the
wireless ping spike symptom it won't stop on it's own unless the computer is
manually restarted.  Then after a while the pings will *spontaneously* start
spiking again after an unknown trigger.

So what is it supposed to look like? My home network is running a 802.11ac
wireless router and my computer is similarly equipped with an ac1200 network
adapter and both are from commodity equipment vendors with a vintage of around 2015 or 2016.

## Normal Wireless Behaviour

When the system is running correctly (which is usually the case) a simple 
ping test will usually look like this:

<video width="100%" autoplay="autoplay" loop="loop">
    <source src="/assets/images/no-ping-spikes.webm" type="video/webm">
</video>

**Note:** I am running the ping to the IP of my wireless router rather than
to a source on the public Internet to try and avoid connection jitter and to
demonstrate that the issue is local to my personal environment.
{: .notice--info}

## Other people with the same problem

Hitting google with a quick search shows plenty of people have been
experiencing very similar issues going back right to the original deployment
of Windows 10.

{% include figure image_path="/assets/images/ping-spike-search.png"
alt="I'm not the only one, other people have ping spike problems"
caption="I'm not the only one, other people have ping spike problems" %}

Reading some of the problem reports and posts suggest that the issue has
something to do with Windows 10 periodically making the wireless adapter
search for other wireless networks in the area. Moreover several posts
suggest a workaround that will mitigate the issue at the expense of being
unable to search for new wireless networks in the area.

## Work around for Wireless Ping Spikes on Windows 10

The suggested workaround is to turn of WLAN autoconfig which will prevent
Windows from searching for new wireless networks in the area.

The first thing is to figure out the name of the wireless adapter, for me
it's Wi-Fi as indicated looking through Network Connections. Mine is bridged
since I sometimes like to plug in physically networked machines into the my
wifi network (removing the bridge doesn't solve the issue, I've tested).

{% include figure image_path="/assets/images/network-adapter.png"
alt="Identifying the wireless network adapter"
caption="Identifying the wireless network adapter" %}

From here the command is pretty simple, from an Administrator Command Prompt
window, just run

```
netsh wlan set autoconfig enabled=no interface="Wi-Fi"
```

From here my pings return to normal but I'm not longer able to search for
new wireless networks, nor am I able to rejoin my normal wireless network
without temporarily re-enabling autoconfig for the interface.

## Permanent solution for Ping Spikes?

Well, at the moment (October 2020) I don't have a solution that is permanent
and will just work normally. Honestly it seems like a windows bug to me
rather than user error since the computer works completely fine most of the
time, but it's also been a long standing issue and I hope that someone will
look into it.

If people want to reach out to me my contact information is listed on the
left and I'm happy to test or experiment with my setup here.

