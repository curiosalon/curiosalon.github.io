---
title: "Thoughts on using FFMPEG instead of Davinci Resolve"
date: 2020-04-21
categories:
  - blog
tags:
  - FFMPEG
  - Wizardry 7
---
Drawing a map is Hard!
======================

{% include figure image_path="/assets/images/davinci-resolve-wizardry7.png"
alt="Editing my wizardry 7 letsplay video in Davinci Resolve"
caption="Editing my wizardry 7 letsplay video in Davinci Resolve" %}

If you've watched my YouTube series on Wizardry 7 that I have been slowly
producing over the past several months you might have noticed that I have
added a map element to the videos that is otherwise not available in the game.
Wizardry 7 has a large world and although the game does have a map built-in,
the mechanism by which you access it is quite cumbersome and requires multiple
menus and clicks, and more importantly there is no way to keep the map open
whilst the player navigates and explores the world.

{% include figure image_path="/assets/images/wiz7-phoonzang-statue.jpg"
alt="Wizardry 7 gameplay with map element composited into video"
caption="Wizardry 7 gameplay with map element composited into video" %}

Several out of game tools exist that read the game state from
inside the DOSBox client and create an external map window which players can
use to navigate.  The solution I use was written by a guy calling himself
Madgod, and works reasonably well.  Though you need to play in "windowed" mode
to be able to see the map window.

Since I have recorded the game as means to entertain myself and
document some digital art that was super important to me growing up, I have
wanted to include the map element in my videos.  Making the map seamlessly
show up as if it was a natural part of the gameplay is a challenge that
I have struggled with for several months now.

My solution has been to composite the cropped and masked map into a compass
style UI element which I fade in and out of view in my videos depending on
context. For instance, the map disappears during combat, or while accessing
the save/loading screens.

{% include figure image_path="/assets/images/wiz7-mapcompass-v2-resolve.png"
alt="Composited Wizardry 7 Map"
caption="Composited Wizardry 7 Map" %}

Since I am doing this strictly at the hobby level, I have invested absolutely
no real life money into the project, so my tools at hand are the free version
of Davinci Resolve (16.2 at the time I am writing these words), OBS, Audacity
and FFMPEG. Of these, Resolve is of course a commercially developed editing
suite and is reasonably powerful but extremely resource intensive.  Indeed,
the Resolve software makes my computer grind to a crawl doing what I would
consider as a reasonably simple composition using the built-in Fusion tool.

To make matters worse, Davinci Resolve crashes on me all the time, at least
once or twice per editing session.  I'm not entirely certain what is causing
the problems for me, but the problems are severe enough to trigger driver
level faults which reset the entire Windows display pipeline and cause any
programs that lean on it heavily (web browsers, games, discord windows, steam
clients) to glitch out to some degree.  I've tolerated the problems
since I don't use the workstation commercially and the hobby aspect of what
I have done has allowed me to justify the headache to myself.

On the other hand, FFMPEG is absolutely rock solid at editing and rendering
video pipelines but obviously doesn't come with a fancy UI to crash once or
twice a day.  If you haven't used the tool before, it's an open source, free
software thingy that has glued the majority of modern video processing
tech into it's 65Mb binary executable.  The feature set is impressive to say
the least about it, but like I said, it doesn't come with a fancy UI (User
interface).

Without diving into the whats and wherefores of Davinci Resolve, my computer
struggles to give enough oomph to run the Fusion compositor despite my
best efforts.  Most recently this came to a head while editing the 11th
episode of my Wizardry 7 series.  I designed a nice Fusion macro to transform
the out of game map source to a stylish video element with alpha blending.
I can easily apply this macro to any map source file I generate, it seemed
that everything was peachy!

{% include figure image_path="/assets/images/wiz7-render-w-fusion-map.png"
alt="Slow video rendering in Davinci Resolve"
caption="Slow video rendering in Davinci Resolve" %}

Except, the performance is terrible. All I am doing is drawing a couple
circles and masking out a small area from the video clip (228 x 228 pixels)
and now playback stutters horribly within the Resolve application suite while
trying to render my little map thingy into the video. So until I buy a new
(computer which won't happen any time soon) I am stuck with either
making do with the terrible application performance and regular crashes, or
I can make my life more exciting by diving into the FFMPEG tool to pre-render
my composited map image.

So lets start to dive into what I know about FFMPEG and see if we can cobble
together the what I need to turn my maps into a beautiful pre-rendered
video element that I can dump into Davinci Resolve (or some other) editing
tool.

First, FFMPEG commands work by setting up what is known as a *Filter Graph*.
Indeed the Davinci Fusion tool works in almost the same way, if you are
familiar with how it's node based compositor works.  Actually, for all I know
Fusion and Resolve may be literally using some version of ffmpeg underneath
the glossy shell (or not, I don't know or particularly care).  As I understand
it, the tool works by setting up a graph (mathematical graph) of operations
and following the graph from a starting node throughout all connected nodes
in the graph.

Actually, and I think this is remarkably cool, you can export the results of
every node in the filter graph to its own distinct output file or stream
so it's possible to debug complicated instruction sets by just saving
the results to a file at any given point in the instructions.  You can give
nodes names so that you can use their input and outputs later from other
nodes.  In fact, it is by using these node names that you create the graph of
instructions that the program will follow since each node generally only
knows about what to do with its inputs and outputs by what they are called.

It seems to me that since I've been able to create a reasonable implementation
of the masking process in Resolve's Fusion tool, I should be able to recreate
that in FFMPEG, assuming I manage to grasp its instruction set.  Basically,
I just need to replicate the process I used in Fusion, inside of my FFMPEG
commands.


Requirements
------------

So let's think about some requirements for what I would like to carry out one
at a time.

> Don't want to stop using Resolve, but I do want fast/stable editing

Resolve is good software, and unlike literally any other comparable suite from
any other major developer is provided for free to hobbyists with a massive
feature set.  I genuinely am truly thankful for it being made available! That
being said, my personal setup isn't powerful enough to use some of its power
without breaking my computer :sadface: .

> I want a pre-rendered video of a nice map I can quickly overlay during edits

What I would like is just an easy to plunk map element for my old computer
game videos.  I don't mind front end complexity, but when it comes to actually
producing something for the YouTube that is conceivably watchable, well, I
strongly prefer to be able to actually use the editing software and not
wait for it to catch up or crash. Like I said in my earlier point, if it was
working smoothly with my current setup, I would just continue to use it. It's
not so I am investigating my options.

> Transparent video so Resolve won't need to chroma key or think for itself

This is a slightly more complicated topic that gets into the technical
requirements of my little project here.  Video codecs that are in use today
almost entirely do not support an Alpha channel, with only a couple of
exceptions (Namely, VP9 from Google and Prores 4444 from Apple). There are
possibly some other exceptions to that statement like an animated collection
of PNG files in some sort of AVI container or something but this would need
a large file size I'm not certain I want to entertain (again old workstation
issues coming up here).

My idea is this, I want 1080p or 720p or whatever resolution transparent video
that has the map element correctly placed inside of it so I literally just
need to drag it into my editor of choice in a layer above my actual video
content.  Since it's transparent except for my little map thingy, it will
just seamlessly overlay my video and nobody, including Resolve or whatever
editor I am using will need to think about it except for managing the alpha
blending.

> Scriptable batch command for automating the pre-render work

Uh, yeah.  This is pretty obvious I think.  Once I figure out the magic FFMPEG
wizardry that is necessary to create a transparent alpha mask video, I'm going
to just create a small script that I can use to automate the entire thing so
that I never need to think about it again and can get on with the important
work of playing computer games from the 90's

> I want one, or maybe two files I can drag into the editor after rendering

Yeah, again this is simple.  When I go to edit these videos I just want to be
able to create the necessary pre-rendered inputs automatically and without the
headache of having to figure it out.  I would actually like to finish my
wizardry series, and having that dumb map thingy in the corner is taking up
a non-trivial amount of my life!

What's Next?
------------

Next time I'm going to start creating the FFMPEG filtergraph instructions
to composite my map thingy together. I'll explain the process by which I
go through one instruction at a time until we are able to reproduce the what
the same (or better) quality of map thingy that I built-in Davinci Resolve.

Take care for now!
