---
title: "Following five bit routines through Wizardry VI and VII"
excerpt: "Five small functions survive between two Wizardry games with identical instruction bodies. Rebuilding them gives us a working recipe and a more interesting question about where they come from."
categories: [Blog]
tags: [Wizardry, Reverse Engineering, DOS]
published: true
toc: false
---

I am, I think, a bit of a lunatic. For an experiment I was playing with one of the fancy language model agents and asked it to go dismantle one of my childhood computer games (Wizardry 7) and tell me what's in there. It did an astonishingly good job, decoding pictures, audio, maps, and all sorts of intricate details I never knew existed in the original game. It was also deeply half-assed in how it went about its work. So like, cool, I'm glad that works, but there is something I've been wanting to learn, and that is actual reverse engineering.

Well then, I tried my hand at having one of the agents decompile the actual executable, and honestly it was really bad at it. Like really really bad.

I watched it burn through tokens at an astonishing rate just trying to reverse engineer the implementation of the C printf library call. Like... ok, I guess I didn't ask it nicely enough to not waste its time on such frivolities. At least start with the game's main routine or something like a nice little edge case function.

For those that don't know, printf is a bit of a monster. It's not surprising it struggled.

There are tools for this, Ghidra, a fancy Java tool, as well as a slew of others, and honestly I thought it would do better than it did. Maybe it needed better prompts or just more dump trucks of coal powered electricity.

No. It actually needed me, thankfully I suppose. I will say the agents make a lot of the monotonous actions of this kind of thing simpler. But they would struggle incredibly hard trying to get to the end of this kind of project without someone like me saying something like wtf every few minutes.

So here's a snippet from my life last night:

I'm trying to reconstruct C source from the Wizardry binaries, and five little functions are making the whole exercise much more difficult than I expect. Most routines give me something I can recognise. These have an odd arrangement of instructions that doesn't seem to fit the usual patterns that all the other functions have. They are just a little weird.

They are 289 bytes in Wizardry VII. They write a bit, read a bit, write a field, read a field, and extract some digital goo from a number. I can explain what they do, and so can the agent. This is bit field manipulation. Getting back to original C source that compiles into those particular instructions is where the trouble starts.

Even a high powered language model gets stuck on this. It can produce perfectly reasonable C that does the same calculation, then spend ages trying to persuade an old compiler to arrange the instructions like the original. Eventually it more or less shrugs its digital shoulders.

## A little room for a lot of flags

Suppose we have a collection of yes or no values to store. We can give each one a whole byte, or pack eight of them into the eight bits of a byte. The second arrangement saves space, but now reading a value involves finding the right byte and picking out the right bit. That probably sounds complicated if you don't know anything about how we get computers to handle numbers. Well, the good news is that it's going to get way more complicated.

The catch is that memory here is addressed in bytes. I can't give the machine an address for just one bit and ask it to replace that. The smallest memory unit these routines read or write is a byte of eight bits. To change one of them, I need to select it inside that byte without having the other seven stick their noses into the calculation.

It's even more complicated because these old computers often work on two bytes together as a word. The bytes are still separate chunks of eight bits, but the whole thing is a bit of a package deal, 16 bits or two sets of eight. Newer computers commonly work on groups of four or eight bytes too.

Sigh........

For example, bit offset 13, counting from zero. Dividing by eight gives us byte index 1 with a remainder of 5. We go to the second byte, then select bit 5 inside it. Reading means testing that bit. Writing means changing it while leaving its neighbours alone. Blah blah blah, here's a picture I had an agent draw showing this:

![Bit offset 13 divided by eight selects byte index 1 and bit position 5, highlighted among the surrounding bits](/assets/images/wizardry-packed-bits/bit-offset.svg)

To set bit 5, I combine the byte with a mask containing a one only at that position. OR with zero leaves a bit alone; OR with one sets it. To clear the selected bit, I use AND with the opposite mask, all ones except a zero at bit 5. The processor still writes a byte, but the mask makes sure only the bit I want changes.

![Setting and clearing bit 5 with highlighted masks, byte values and illustrative OR and AND assembly instructions](/assets/images/wizardry-packed-bits/bit-masks.svg)

*SI points at the selected byte.*

Fields extend the same idea to values that occupy several bits at once. Instead of giving every small number a whole byte or word, we agree on a width and pack the values together. To find a field, these routines first multiply its index by its width, then work out where that bit offset lands in the buffer.

A field can straddle two bytes. Field index 2 with a width of three starts at bit offset 6, so it occupies offsets 6, 7 and 8. The first two positions are in one byte and the third is in the next. Now the routine has to deal with the byte boundary (it's split across two of them) as well as the mask that excludes the unwanted bits.

![A three-bit field starting at buffer offset 6 highlights bits 6 and 7 in byte zero and bit zero in byte one](/assets/images/wizardry-packed-bits/field-boundary.svg)

Once somebody writes these routines, the rest of the game can call them without doing the masks and shifts over again. Finding them together in both games makes me wonder how much of the original library survives between versions.

This is the kind of thing that once you solve it and it works, you damn well don't touch it again.

Neither I nor the coding agent could figure out how this was originally implemented. It wasn't until I started peering even further back into time that it began to become clear. I installed Wizardry 6 (VI for cool kids). But that's foreshadowing. For now we have some puzzling to puzzle over.

## Asking the compiler to do it

The natural place to start is C. These are small operations, and it is easy to write something that reads and writes the right bits.

At one point the language model agent announces, very proudly no doubt, "I solved it!"

Well, not really. It has transcribed the machine code directly into the assembly instructions it represents. A nice trick, but hardly an explanation of where the code comes from. It could just as well give me the original ones and zeros back and say, "see, here ya go dummy why are you even doing this".

Getting the compiler to choose the same instructions keeps going wrong in small ways. Integer promotions (going from 8 bits to 16) change the width of an operation, or a temporary variable ends up in a different register. I can write perfectly sensible C and get working machine code that looks nothing like the original. And, like I said at the outset, I'm a lunatic.

Together with the agent I try different masks and shifts, register declarations, bitfields, unions, helper functions, compiler settings, and older compilers and newer compilers, and even take a nap. Quite a few approaches produce the right logic. There is a ton of equivalent code, just not matching ones and zeros. Some get close enough to make the next experiment seem obvious. It's just a few instructions away, but no..... Then the next experiment moves something else and the puzzle continues.

Eventually it dawns on me that assembly, the proud solution of the agent from hours earlier, is probably the right track, but for a different reason. Whoever wrote the game may be calling a library that already handles all this pushing and pulling of bits. This is complex stuff. It's not the kind of thing you want to do twice after it works. I am trying to reconstruct a C expression when the original programmer may have been calling some hand crafted assembly function all along.

## What changes between the games

In Wizardry VI the same functions occupy 260 bytes instead of the sequel's 289. When I compare them, all 200 bytes doing the actual bit manipulation match, right down to the register choices and awkward little details. The changes are in the setup and cleanup around them. That's weird, right? Like, why are they the same if the rest of the compiled code is different? Hmm, well, let's take a look together.

Here are the five routines side by side. Let's not worry about the details of what they do. It's the goo around them that matters here, because that's the part that's different. The later versions gain either five or seven bytes each.

![Comparison of all five routines in VI and VII, with added setup instructions marked by plus signs and unchanged algorithm bodies identified](/assets/images/wizardry-packed-bits/version-diff.svg)

Every function gains the same five bytes of setup in VII.

```asm
cld
mov ax, ds
mov es, ax
```

The first instruction clears the direction flag. When the processor uses that flag for string operations, clearing it selects the forward direction. The next two instructions copy the data segment register into the extra segment register. We cannot move directly from one segment register to another, so AX acts as the middleman.

The two field functions also gain instructions to save and restore ES. The other three already save it in VI. Five extra bytes in each of five functions gives us 25 bytes, and saving and restoring ES in the remaining two adds another four. There are our 29 bytes.

![The added CLD, MOV AX DS and MOV ES AX instructions explained individually, with the segment value moving through AX and a count of the extra bytes](/assets/images/wizardry-packed-bits/entry-assembly.svg)

The odd part is that the bit manipulation bodies do not need this string setup. Why add it to all five?

A nearby scanner routine already contains a `CLD`, but gains another one at its entry. Now it looks as though the same setup is being applied more broadly. If these functions share an entry macro, changing that macro could add instructions even where the function itself doesn't need them.

Simply linking the same object file again cannot put new instructions inside its functions. Somewhere there has to be a rebuild, an edit, or a different library member.

Okay. Fine. But how are they calling it, and what does that library look like? I can call assembly from C, but the particular arrangement in these functions still doesn't fall out of anything the model or I can persuade the compiler to do.

Clearly some new tools are needed.

## Unleashing my internal angr

At this point I resort to unleashing my internal anger. Well, not anger. [angr](https://angr.io/) actually.

It is a Python framework for analysing programs, with a solver doing something rather useful underneath. I can describe inputs symbolically, follow what the machine code does with them, and ask whether there is an input that makes a proposed reconstruction disagree with the original. The solver machinery, including Z3, lets me reason over millions of input combinations without writing a loop to run each one.

If a candidate fails, I get an input that shows where it fails. That gives the model something to work on beyond staring at another disassembly listing.

But this needs some glue. I am comparing output from an archaic C compiler, with its own vintage dialect, calling conventions and view of a 16 bit machine. Modern angr doesn't arrive with an interface for this particular bit of Wizardry. (See, a joke, get it?) I need to describe the segments, stack, routine boundaries and the machine state.

So, with the help of a language model, I build a tool called [binquery](https://github.com/curiosalon/binquery). BinQuery? Binquery. The repository settles on the lower case version, I guess. It's supposed to be a Unix style tool for doing binary analysis.

I give it the two binaries and a small settings file saying where the routines start, which inputs to try, and what should agree when they finish. angr works through the possibilities, then a second emulator called Unicorn runs any examples where the routines disagree. I can save an example and run it again while I work on the C.

For the function that pulls bits out of a number, I get a C version that compiles to 30 bytes, against 35 in the VI original. Starting both with the same machine state, I ask binquery to compare every 16 bit value, with shifts from 0 through 15 and widths from 1 through 16. That is 16,777,216 combinations for the solver to reason through. The answers agree for all of them. This bit of C is calculating the same result as the original assembly swamp.

It also finds differences in the registers used along the way, and Unicorn reproduces them. So the calculation works, but the compiler is still going about it differently.

When I compare two versions of a bit-reading function, I find something else I would miss by checking the answer alone. Both return the same value, but one reads a byte and the other reads a word. That is an extra neighbouring byte being read, even though it doesn't change the answer in this example.

There is more about how this works in the [binquery notes](https://github.com/curiosalon/binquery/blob/e3997ca808fc4c4e809128269f18161a6841a538/docs/CAPABILITIES.md).

## The tools have their own puzzle

I'm using Manx/Aztec C 4.10d. Figuring out its tools occasionally becomes an investigation of its own. For instance, I had to install a binary patch in my version of it to stomp a decimal to binary conversion bug that I stumbled upon in an earlier adventure. My guess is that this is very close to the version Sir-Tech originally used to write the Wizardry games, probably 4.2.

Reverse engineering the compiler itself exposed hidden diagnostic switches that show more of its internal choices. They look like a shortcut to understanding why a value gets a particular register. Unfortunately, turning them on also changes how the compiler hands its output to the assembler.

So now I spend a bit of time chasing a software build problem caused by the diagnostic tooling setup itself. I open the manual (a scan of the manual) and learn that explicitly giving the assembler `-ZAP` on its command line gets the ordinary output back. I can finally use the extra information without accidentally changing the thing I am investigating.

## A common recipe

As soon as the right switching Wizardry (see, I did it again!?) becomes clear, the reconstruction agent can match both games using one shared assembly macro library. A single `packed_family` macro produces all five functions. The language model even suggests an `ENVIRONMENT` setting to choose the setup for Wizardry VI or VII, should I decide to tackle the rest of Wizardry 6 (VI, to see if you're still with me) next.

Changing that setting gives me the added setup shown in the comparison above.

The four functions that work on memory share the code for finding the right byte and bit. Three functions also share the code that builds their masks. For the setup and cleanup I use macros supplied with the compiler in `LMACROS.H`.

I keep the odd details too, including the writer's stack temporary variable and the reader's use of DI for its mask. Changing those would give me yet another reasonable implementation that doesn't match the original.

From C, I can call the assembly functions like any other functions. A small header file supplies their declarations and a few macros to make the calls convenient.

I build small C programs that call them, run those programs, and compare the compiled routines with both games. All 260 bytes match VI, and all 289 match VII.

The library is now part of the Wizardry VII reconstruction and its Ghidra project. The normal build produces the same bitfield object, with all 289 bytes matching the game.

## Where does it come from?

Of course I can make assembly match when I already have the instructions in front of me. The model's earlier victory lap still doesn't count. But I now have all five routines organised as a library that C can call, and one setting accounts for the differences between games.

My leading guess is a maintained assembly library with shared entry macros or repeated templates. Another possibility is that compiler output becomes assembly source that somebody keeps and edits. C with assembly helpers remains a possibility too, along with an untested compiler configuration or a library object from another toolchain perhaps that was imported to the Wizardry platform.

The extra setup in VII could come from somebody editing a shared macro. That would explain how the same instructions appear in several functions at once, including ones that don't need them.

I would love to find the same routines in another program, especially one with surviving source. Then I might finally get to see what somebody types to make the compiler, or assembler, put those instructions in that peculiar order.

Either way, I'm pretty confident I've reproduced the sort of compiler and assembler interface the original programmers were working with.
