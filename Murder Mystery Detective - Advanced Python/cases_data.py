"""
cases_data.py
--------------
All investigation cases for the Murder Mystery Detective game.
Pure data only - no imports, no dependencies. Each case has:
  title, accent (hex color), story, suspects (name + backstory +
  statement/alibi used by the INTERROGATE feature), killer, a pool
  of clues, and the full solution (why the killer is guilty + why
  every other suspect is innocent).
"""

cases = [
    {
        "title": '( CASE 1 ) THE DARK MANSION INCIDENT',
        "accent": '#7a2b28',
        "story": 'A thunderstorm shakes the isolated Blackwood Mansion.\n\nA billionaire host invites five guests for a private night gathering.\n\nAt exactly 12:00 AM, the lights suddenly go out.\n\nScreams echo in the darkness.\n\nWhen emergency power returns...\n\nThe host is found dead in a locked study room from the inside.\n\nNo forced entry. No witnesses.\n\nOnly fear… and silence that feels intentional.',
        "suspects": [
            {"name": 'Butler John', "backstory": 'Served the family for 25 years. Secret gambling debts.', "statement": 'No comment.'},
            {"name": 'Chef Maria', "backstory": 'Recently fired after a heated argument with the victim.', "statement": 'No comment.'},
            {"name": 'Driver Alex', "backstory": 'Claims he was outside during the entire blackout.', "statement": 'No comment.'},
            {"name": 'Guest Mr. Black', "backstory": 'Unknown man who arrived without invitation.', "statement": 'No comment.'},
            {"name": 'Nurse Elena', "backstory": 'Caring for the victim’s sick wife.', "statement": 'No comment.'},
        ],
        "killer": 'Guest Mr. Black',
        "clues": [
            'Hidden key under carpet near desk',
            'Strange footsteps recorded at midnight',
            'CCTV feed cut exactly at 11:58 PM',
            'Blood trace on library door handle',
            'Missing guest registry page',
            'Fake identity card found in garden soil',
        ],
        "solution": {
            "killer_reason": 'Guest Mr. Black used a fake identity to enter the mansion. The missing registry page, fake ID card, and cut CCTV footage exposed him as the killer.',
            "innocent_reasons": {
                'Butler John': 'His gambling debts made him suspicious, but no evidence connected him to the murder.',
                'Chef Maria': 'She argued with the victim but witnesses confirmed her location during the blackout.',
                'Driver Alex': 'Parking area footage proved he remained outside.',
                'Nurse Elena': "She was caring for the victim's wife and never entered the study.",
            },
        },
    },
    {
        "title": '( CASE 2 ) THE HOTEL SILENCE CASE',
        "accent": '#1f3a5f',
        "story": 'A luxury penthouse suite. A world-famous singer stays overnight.\n\nSecurity cameras operate normally… until 3:33 AM.\n\nFor exactly 7 minutes, all surveillance goes dark.\n\nNo alarms. No movement.\n\nWhen backup footage resumes…\n\nThe singer is found dead on the bed, with no visible struggle.\n\nOnly silence remains as the biggest clue.',
        "suspects": [
            {"name": 'Manager Roy', "backstory": 'Hotel facing severe financial crisis.', "statement": "I was in my office going over the books - the hotel's bleeding money, that's no secret. I never went near her room."},
            {"name": 'Assistant Nina', "backstory": 'Deep jealousy toward the singer.', "statement": 'Jealous? Maybe. Murderous? No. I was crying in the stairwell, if you must know.'},
            {"name": 'Security Mike', "backstory": 'Responsible for CCTV monitoring system.', "statement": 'The cameras cut out for exactly six minutes. I was the only one with the code to the control room.'},
            {"name": 'Room Service Leo', "backstory": 'Delivered drinks shortly before death.', "statement": 'I brought up her drink and left. She was very much alive when I shut that door.'},
            {"name": 'Unknown Caller', "backstory": 'Last person to contact the victim.', "statement": "We spoke for two minutes. She sounded frightened of someone. It wasn't me."},
        ],
        "killer": 'Security Mike',
        "clues": [
            'CCTV manually overwritten during blackout',
            'Poison residue in champagne glass',
            'Deleted phone call logs',
            'Elevator override detected',
            'Duplicated keycard access trace',
        ],
        "solution": {
            "killer_reason": 'Security Mike manipulated the CCTV system, deleted surveillance records, and used duplicated access credentials.',
            "innocent_reasons": {
                'Manager Roy': 'He had financial problems but no evidence placed him inside the suite.',
                'Assistant Nina': 'She was jealous of the singer but had no opportunity to commit the crime.',
                'Room Service Leo': 'He delivered drinks and left before the murder occurred.',
                'Unknown Caller': 'The caller was suspicious but had no physical access to the victim.',
            },
        },
    },
    {
        "title": '( CASE 3 ) UNIVERSITY LAB EXPLOSION',
        "accent": '#1f5f52',
        "story": 'A prestigious university chemistry lab. Late-night research is ongoing.\n\nA sudden explosion destroys the entire laboratory section.\n\nA top student is found dead among broken glass and chemical fire.\n\nAuthorities confirm:\n\nThe formula was altered minutes before the reaction.',
        "suspects": [
            {"name": 'Lab Tom', "backstory": 'Controls chemical storage access.', "statement": "I signed out the chemical cabinet key at 9pm and returned it at 9:15. The logs would show it, if they hadn't been wiped."},
            {"name": 'Student Jake', "backstory": 'Rival researcher competing academically.', "statement": "Rival? We were competing for the same grant, that's all academia is. I was in the library till midnight."},
            {"name": 'Professor Smith', "backstory": 'Strict supervisor of the lab.', "statement": 'I run a tight lab. I was grading papers in my office the entire evening.'},
            {"name": 'Lab Assistant Mia', "backstory": 'Manages lab equipment and keys.', "statement": 'I checked the equipment at 8, locked up at 9, and went home. Everything was normal.'},
            {"name": 'Cleaner Bob', "backstory": 'Works night shift cleaning labs.', "statement": 'I clean floors, not test tubes. I was three buildings over when it happened.'},
        ],
        "killer": 'Lab Tom',
        "clues": [
            'Incorrect chemical mixture discovered',
            'Burned protective gloves near sink',
            'Storage cabinet left unlocked',
            'Missing experiment notebook pages',
        ],
        "solution": {
            "killer_reason": 'Lab Tom altered the chemical mixture and had direct access to the storage cabinet.',
            "innocent_reasons": {
                'Student Jake': 'He was a rival researcher but had no access to the chemicals.',
                'Professor Smith': 'He was supervising elsewhere during the incident.',
                'Lab Assistant Mia': 'No evidence linked her to the altered formula.',
                'Cleaner Bob': 'He worked nearby but lacked the knowledge to sabotage the experiment.',
            },
        },
    },
    {
        "title": '( CASE 4 ) BANK VAULT MURDER',
        "accent": '#1f5f33',
        "story": 'A high-security bank vault. No one is supposed to enter without biometric clearance.\n\nYet the bank manager is found dead inside the vault room.\n\nSecurity logs show NO forced entry.\n\nMoney remains untouched…\n\nBut confidential documents have disappeared.',
        "suspects": [
            {"name": 'Guard Henry', "backstory": 'Night shift security guard.', "statement": 'I did my rounds every thirty minutes, same as always. I found her already like that.'},
            {"name": 'Clerk Sara', "backstory": 'Recently promoted bank employee.', "statement": "I was promoted last month - why would I risk that? I was at my desk reconciling the day's deposits."},
            {"name": 'Cleaner Bob', "backstory": 'Has access to master keys.', "statement": 'Master keys, sure, but I never go near the vault floor. Ask anyone.'},
            {"name": 'IT Officer Dan', "backstory": 'Manages security system logs.', "statement": "The security logs show a gap I can't explain. I was watching the monitors, I swear it."},
            {"name": 'Visitor Mr. X', "backstory": 'Unknown man seen briefly inside bank.', "statement": 'I was there to open an account, nothing more. I left before closing.'},
        ],
        "killer": 'Clerk Sara',
        "clues": [
            'Security logs manually deleted',
            'Fake keycard authentication used',
            'Vault camera footage looped',
            'Hidden USB found in manager desk',
        ],
        "solution": {
            "killer_reason": 'Clerk Sara used fake authentication, stole confidential documents, and erased evidence from security logs.',
            "innocent_reasons": {
                'Guard Henry': 'Security logs showed he remained at his assigned post.',
                'Cleaner Bob': 'He had key access but no connection to the missing documents.',
                'IT Officer Dan': 'He maintained systems but did not alter the vault records.',
                'Visitor Mr. X': 'He appeared suspicious but never entered the vault area.',
            },
        },
    },
    {
        "title": '( CASE 5 ) HOSPITAL NIGHT SHIFT DEATH',
        "accent": '#2b5f5f',
        "story": 'A quiet hospital during night shift.\n\nA patient receiving routine injection suddenly dies within minutes.\n\nDoctors claim equipment failure.\n\nBut the syringe tells a different story.\n\nSomething was changed when no one was watching.',
        "suspects": [
            {"name": 'Nurse Kate', "backstory": 'Experienced night duty nurse.', "statement": 'I checked his chart at 11, everything was in order. I was on my rounds the rest of the night.'},
            {"name": 'Doctor Ray', "backstory": 'Senior doctor on shift.', "statement": 'I signed off shift at 10:30. I was asleep in the on-call room after that.'},
            {"name": 'Intern Josh', "backstory": 'New trainee handling medications.', "statement": 'I gave him his medication exactly like the chart said. I followed procedure. I did.'},
            {"name": 'Pharmacist Lily', "backstory": 'Responsible for medicine storage.', "statement": "I dispense what's prescribed. I don't decide dosages. I was in the pharmacy the whole shift."},
        ],
        "killer": 'Intern Josh',
        "clues": [
            'Wrong medicine label detected',
            'Injection syringe replaced',
            'Missing patient treatment file',
            'Tampered dosage record',
        ],
        "solution": {
            "killer_reason": 'Intern Josh replaced the syringe and altered the dosage records.',
            "innocent_reasons": {
                'Nurse Kate': 'She followed hospital procedures correctly.',
                'Doctor Ray': 'He prescribed the correct treatment.',
                'Pharmacist Lily': 'Medicine inventory records proved she supplied the correct drugs.',
            },
        },
    },
    {
        "title": '( CASE 6 ) AIRPORT MIDNIGHT DISAPPEARANCE',
        "accent": '#5f3d1f',
        "story": 'An international airport. Busy terminals at midnight.\n\nA passenger enters security checkpoint… but never exits.\n\nNo boarding record. No exit scan.\n\nOnly one blind spot exists in CCTV coverage.\n\nAnd that is where the truth disappears.',
        "suspects": [
            {"name": 'Security Paul', "backstory": 'CCTV control operator.', "statement": 'I watched the monitors all night. The feed near gate 12 glitched right when he vanished.'},
            {"name": 'Passenger Leo', "backstory": 'Last seen arguing at gate.', "statement": 'We argued, yes. About a delayed flight. I never touched him after that.'},
            {"name": 'Staff Emma', "backstory": 'Handles luggage transport.', "statement": "I was moving luggage between terminals. I didn't even see him after check-in."},
            {"name": 'Pilot Rick', "backstory": 'Arrived from international flight.', "statement": "I'd just landed from an international flight. I was still clearing customs when this happened."},
        ],
        "killer": 'Passenger Leo',
        "clues": [
            'CCTV blind spot exploited',
            'Missing passport report',
            'Spilled coffee near boarding gate',
            'Fake boarding pass found',
        ],
        "solution": {
            "killer_reason": 'Passenger Leo exploited the CCTV blind spot and used a fake boarding pass.',
            "innocent_reasons": {
                'Security Paul': 'No evidence showed he manipulated the cameras.',
                'Staff Emma': 'She was handling luggage in another terminal.',
                'Pilot Rick': 'Flight records confirmed his location during the incident.',
            },
        },
    },
    {
        "title": '( CASE 7 ) CRUISE SHIP MYSTERY DEATH',
        "accent": '#1f3f5f',
        "story": 'A luxury cruise ship sailing in the middle of the ocean.\n\nA passenger is reported missing during the night.\n\nSearch begins immediately.\n\nOnly broken railing near the deck is found.\n\nNo body… only silence over the ocean waves.',
        "suspects": [
            {"name": 'Captain Holt', "backstory": 'Controls entire ship navigation.', "statement": 'I was on the bridge the entire night, as the log will confirm.'},
            {"name": 'Chef Bruno', "backstory": 'Works in ship kitchen.', "statement": 'The kitchen closes at midnight. I was cleaning down after service.'},
            {"name": 'Passenger Mia', "backstory": 'Last seen arguing with victim.', "statement": 'We argued about money he owed me, not enough to kill over. I went straight to my cabin.'},
            {"name": 'Engineer Luke', "backstory": 'Controls ship mechanical systems.', "statement": 'I was below deck all night, the engines needed constant attention in that storm.'},
        ],
        "killer": 'Passenger Mia',
        "clues": [
            'Broken railing on upper deck',
            'Missing life jacket',
            'Disabled deck camera feed',
            'Wet footprints near stairs',
        ],
        "solution": {
            "killer_reason": 'Passenger Mia argued with the victim and disabled the deck camera before the crime.',
            "innocent_reasons": {
                'Captain Holt': 'Navigation logs confirmed he remained on the bridge.',
                'Chef Bruno': 'Kitchen staff verified his presence during the incident.',
                'Engineer Luke': 'He was working in the engine room at the time.',
            },
        },
    },
    {
        "title": '( CASE 8 ) OLD LIBRARY SECRET DEATH',
        "accent": '#4a2f1f',
        "story": 'A historic library filled with ancient books and forgotten knowledge.\n\nA researcher is found dead inside a locked reading room.\n\nNo forced entry is detected.\n\nBut one ancient manuscript has vanished.\n\nAnd the library is hiding more than books.',
        "suspects": [
            {"name": 'Librarian Anna', "backstory": 'Manages restricted archives.', "statement": 'I catalogued the archive room and went home early. Nothing seemed out of place.'},
            {"name": 'Researcher Tom', "backstory": 'Studying ancient manuscripts.', "statement": "I was studying that manuscript for weeks. I just needed more time with it than they'd allow."},
            {"name": 'Student Emma', "backstory": 'Visiting scholar.', "statement": 'I was in the east reading room the whole evening, ask the other students.'},
            {"name": 'Janitor Mike', "backstory": 'Night cleaning staff.', "statement": "I found the broken lock on my rounds. That's when I called it in."},
        ],
        "killer": 'Researcher Tom',
        "clues": [
            'Missing ancient manuscript',
            'Hidden bookshelf passage',
            'Ink stains on gloves',
            'Broken lock mechanism',
        ],
        "solution": {
            "killer_reason": 'Researcher Tom murdered the victim to obtain the ancient manuscript and used the hidden passage to escape.',
            "innocent_reasons": {
                'Librarian Anna': 'Archive records showed no suspicious activity from her.',
                'Student Emma': 'She was studying in another section of the library.',
                'Janitor Mike': 'He discovered evidence but was not involved in the crime.',
            },
        },
    },
    {
        "title": '( CASE 9 ) THEATER BACKSTAGE MURDER',
        "accent": '#3a1f2b',
        "story": 'Opening night at the Ravenwood Theater is minutes from its curtain call.\n\nThe lead actor is found behind the velvet curtains, struck down by what was supposed to be a harmless stage prop.\n\nSomehow, the prop dagger had been swapped for a real blade.\n\nThe show must go on - but first, the killer must be found.',
        "suspects": [
            {"name": 'Director Vince', "backstory": 'Obsessed with a flawless opening night.', "statement": "I was pacing the wings, going over cues. Opening night nerves, that's all it was."},
            {"name": 'Understudy Claire', "backstory": 'Has waited three years for the lead role.', "statement": 'I was warming up my voice in the dressing room. I barely touched that prop table.'},
            {"name": 'Stage Manager Owen', "backstory": 'Responsible for checking every prop before curtain.', "statement": 'I checked every prop myself before curtain. Everything was where it should be... I thought.'},
            {"name": 'Costume Designer Priya', "backstory": 'Was seen arguing with the victim about a torn costume.', "statement": 'I was fixing a torn hem two minutes before it happened. Ask the seamstress.'},
            {"name": 'Rival Actor Felix', "backstory": 'Long-standing professional rivalry with the victim.', "statement": 'We hated each other professionally, sure. But I wanted to beat him on stage, not off it.'},
        ],
        "killer": 'Understudy Claire',
        "clues": [
            'A threatening note found crumpled in the dressing room bin',
            "The real dagger's sheath hidden inside the understudy's costume trunk",
            "A costume button missing from the victim's torn sleeve, matching one on Claire's coat",
            'The backstage camera schedule shows a five-minute blind spot near the prop table',
            "A worn theater program with the lead role's lines heavily rehearsed in Claire's handwriting",
        ],
        "solution": {
            "killer_reason": 'Claire swapped the prop dagger for a real one during the camera blind spot. After three years as understudy with the tour about to end, this was her last chance at the lead role - and she took it in the cruelest way possible.',
            "innocent_reasons": {
                'Director Vince': 'Multiple cast members confirm he was pacing the wings in full view the entire time.',
                'Stage Manager Owen': 'His prop checklist, signed and timestamped, shows the dagger was still fake twenty minutes before the murder.',
                'Costume Designer Priya': 'The seamstress confirms she was helping Priya with a costume repair at the time of the murder.',
                'Rival Actor Felix': 'Felix was warming up on the opposite side of the stage, seen by half the cast.',
            },
        },
    },
    {
        "title": '( CASE 10 ) CASINO MIDNIGHT FRAUD',
        "accent": '#3a2b0f',
        "story": "A high-stakes gambler wins the largest hand the Golden Star Casino has ever paid out - then collapses dead in the private VIP room minutes later.\n\nThe house doesn't like losing. But did someone make sure he never got to spend it?\n\nThe chips are down, and it's time to find out who's cheating - and who's killing.",
        "suspects": [
            {"name": 'Pit Boss Carla', "backstory": 'Oversees every table and every dollar that moves through the floor.', "statement": 'I was walking the floor like every night. I never went near the VIP room.'},
            {"name": 'Dealer Sam', "backstory": "Dealt the victim's final, suspiciously lucky hand.", "statement": "I dealt his last hand and walked away. What he drank after that wasn't my business."},
            {"name": 'Bartender Nico', "backstory": "Prepared the victim's final drink personally.", "statement": "I made that drink exactly to order. I don't know what ended up in it."},
            {"name": 'Bodyguard Trent', "backstory": 'Hired by the victim for protection that night.', "statement": 'I was posted right outside the door. No one suspicious went in, that I saw.'},
            {"name": 'Rival Gambler Diane', "backstory": 'Lost a fortune to the victim earlier that night.', "statement": 'I lost big to him that night. I was still at my table when it happened, ask the dealer.'},
        ],
        "killer": 'Pit Boss Carla',
        "clues": [
            "A rigged card deck with faint marks found in the pit boss's office",
            "Trace poison residue in the VIP room's discarded glass",
            'A hidden accounting ledger showing years of skimmed casino profits',
            'A staff keycard log showing Carla badged into the VIP room after hours',
            "A torn note in the victim's pocket demanding an explanation for the missing money",
        ],
        "solution": {
            "killer_reason": 'Carla had been skimming casino profits for years through rigged tables. The victim discovered her fraud and confronted her with proof, so she poisoned his celebratory drink to silence him before he could go to the owners.',
            "innocent_reasons": {
                'Dealer Sam': 'Security footage shows Sam clocked out and left the building before the drink was poisoned.',
                'Bartender Nico': 'Nico prepared dozens of drinks that night; the poison was added after his drink left the bar, in the VIP room itself.',
                'Bodyguard Trent': "Trent's post outside the door means he would have seen anyone but the badge-holder enter - and only Carla's keycard was used.",
                'Rival Gambler Diane': 'Diane was still seated at her table, confirmed by the dealer and pit cameras, when the drink was poisoned.',
            },
        },
    },
    {
        "title": '( CASE 11 ) SKI RESORT AVALANCHE COVER-UP',
        "accent": '#0f2a3a',
        "story": 'A resort owner is found dead at the base of the north slope, officially ruled a tragic avalanche accident.\n\nBut a young ski instructor swears the safety rope was cut, not snapped by snow.\n\nWith a shady land deal on the table and a storm erasing evidence by the hour, the truth is buried deeper than the body was.',
        "suspects": [
            {"name": 'Resort Manager Greta', "backstory": "Handling the resort's storm closure that night.", "statement": 'I was in the lodge handling the storm closure. I never went near that slope.'},
            {"name": 'Ski Instructor Finn', "backstory": 'Reported a frayed safety rope the day before.', "statement": 'I saw the rope was frayed the day before and reported it. No one listened.'},
            {"name": 'Rescue Patroller Sam', "backstory": 'Was delayed reaching the scene by a redirected radio call.', "statement": 'My radio call got redirected - I swear I responded the second I heard.'},
            {"name": 'Investor Mr. Cho', "backstory": 'About to lose a lucrative land deal with the victim.', "statement": 'Business is business. I had no reason to harm a man I needed alive to sign papers.'},
            {"name": 'Chef Oliver', "backstory": "Was prepping the lodge's dinner service all afternoon.", "statement": 'I was prepping dinner service in the lodge kitchen all afternoon.'},
        ],
        "killer": 'Investor Mr. Cho',
        "clues": [
            'The safety rope shows a clean, deliberate cut rather than a snapped fray',
            "Forged pages found in the land deal contract, backdated before the victim's death",
            "Footprints leading away from the marked trail toward the investor's cabin",
            'The rescue patrol radio log shows a call was redirected minutes before the fall',
            "A burner phone in Mr. Cho's coat with texts arranging the 'accident'",
        ],
        "solution": {
            "killer_reason": "Mr. Cho had forged contract pages for a land deal the victim was about to cancel. He cut the safety rope and redirected the rescue patrol's radio call to delay help, because losing that deal would have ruined him financially.",
            "innocent_reasons": {
                'Resort Manager Greta': 'Lodge staff confirm Greta was on the phone with the county about the storm closure the entire time.',
                'Ski Instructor Finn': "Finn's written report about the frayed rope, filed the day before, shows he tried to prevent this, not cause it.",
                'Rescue Patroller Sam': "Sam's radio call was proven to be redirected by someone else's device, not tampered with by Sam himself.",
                'Chef Oliver': 'Kitchen staff and delivery logs confirm Oliver never left the lodge kitchen that afternoon.',
            },
        },
    },
    {
        "title": '( CASE 12 ) ART GALLERY HEIST MURDER',
        "accent": '#2b0f3a',
        "story": "On the night of its biggest exhibition, the Lumière Gallery loses both its star curator and its priceless centerpiece painting.\n\nThe curator is found dead among the guests' abandoned champagne glasses.\n\nThe painting is gone. But is this a heist gone wrong, or something far more personal?",
        "suspects": [
            {"name": 'Gallery Owner Renée', "backstory": "Staked her reputation on this exhibition's success.", "statement": "The exhibit was my life's work. I was greeting guests all evening, dozens saw me."},
            {"name": 'Art Restorer Felix', "backstory": 'Had private, unsupervised access to the painting for months.', "statement": "I restore paintings, I don't fake them. I was in my studio finishing unrelated work."},
            {"name": 'Security Guard Omar', "backstory": "Responsible for the gallery's camera system that night.", "statement": "I did my rounds on schedule. The east wing camera glitch wasn't my doing."},
            {"name": 'Journalist Priya', "backstory": 'Was covering the exhibition for a major art magazine.', "statement": 'I was interviewing collectors for my piece. I barely knew the curator.'},
            {"name": 'Wealthy Collector Mr. Vane', "backstory": 'Had made an aggressive bid for the missing painting.', "statement": 'I came to bid on the painting, not steal it. I can afford the real thing.'},
        ],
        "killer": 'Art Restorer Felix',
        "clues": [
            'Brushstroke analysis proving the displayed painting was a forgery',
            "Frame screws that don't match the gallery's original hardware",
            "A torn page from the curator's notebook reading 'confront F. tonight'",
            "A canvas supplier receipt found in the restorer's studio, dated weeks before the show",
            "Solvent residue on the restorer's cuffs matching the type used to age forged paintings",
        ],
        "solution": {
            "killer_reason": 'Felix had spent months secretly forging the centerpiece painting while it was in his care for restoration. The curator discovered the forged copy hidden in his studio and confronted him the night of the exhibition, so he killed her to protect the secret and fled with the original.',
            "innocent_reasons": {
                'Gallery Owner Renée': 'Dozens of guests and photographs place Renée greeting visitors at the exact time of the murder.',
                'Security Guard Omar': "Omar's rounds log and a guest's photo both place him in the west wing during the murder.",
                'Journalist Priya': "Priya's recorded interviews time-stamp her across the room, speaking with three separate collectors.",
                'Wealthy Collector Mr. Vane': "Mr. Vane's bid was on record before the show even opened - he had no need to steal what he could simply buy.",
            },
        },
    },
    {
        "title": '( CASE 13 ) NIGHT TRAIN EXPRESS MYSTERY',
        "accent": '#1f2b3a',
        "story": 'The overnight express races through the dark countryside when a wealthy businessman is found dead in his locked sleeper cabin.\n\nThe door was bolted from the inside. The window barely opens a crack.\n\nSomewhere among the sleeping passengers is someone who found a way in - and out - without anyone noticing.',
        "suspects": [
            {"name": 'Conductor Grace', "backstory": 'Holds the only spare master key to every cabin.', "statement": "My master key never left my belt. I'd stake my job on it, which I suppose I am."},
            {"name": 'Assistant Theo', "backstory": "Managed the victim's business affairs and finances.", "statement": 'I brought him his tea and left for my own cabin. He was alive when I shut that door.'},
            {"name": 'Fellow Passenger Mrs. Ahn', "backstory": 'Occupied the cabin next door, awake late into the night.', "statement": 'I heard raised voices earlier, but I was asleep by the time it happened.'},
            {"name": 'Chef Car Cook Benny', "backstory": "Prepared and served the victim's evening meal.", "statement": "I was cleaning the dining car. I didn't even know which cabin was his."},
            {"name": 'Stranger in Cabin 4', "backstory": 'Boarded at the last stop with no clear itinerary.', "statement": "I boarded at the last station. I don't know this man from anyone."},
        ],
        "killer": 'Assistant Theo',
        "clues": [
            "The conductor's spare master key is missing from its locked cabinet",
            'Altered pages in the company ledger hiding months of embezzled funds',
            "Sleeping pill residue found in the victim's teacup",
            'The cabin window latch shows fresh tampering marks from outside',
            'A torn boarding pass stub proving Theo left and re-entered his own cabin twice that night',
        ],
        "solution": {
            "killer_reason": "Theo had been embezzling from the victim's company for over a year. The victim had just discovered the altered ledger and planned to report him to the board first thing in the morning, so Theo drugged his tea, used the missing spare master key to get in, and staged the cabin to look sealed from the inside.",
            "innocent_reasons": {
                'Conductor Grace': "Grace's key was checked out and logged at every stop except the one where it went missing from the cabinet, which points away from her.",
                'Fellow Passenger Mrs. Ahn': "Mrs. Ahn's cabin door was found bolted from the inside all night, confirmed by the conductor's early morning rounds.",
                'Chef Car Cook Benny': 'Benny was seen by three other staff members cleaning the dining car for the entire window of the murder.',
                'Stranger in Cabin 4': "The stranger's ticket shows they boarded after the estimated time of death.",
            },
        },
    },
    {
        "title": '( CASE 14 ) RADIO STATION LATE NIGHT KILLING',
        "accent": '#3a0f1f',
        "story": "Moments after signing off his controversial late-night show, a radio host is found dead in the studio - the microphone still live, broadcasting silence to thousands of listeners.\n\nHe'd made plenty of enemies with his on-air exposés.\n\nNow it's time to go live with the truth about who silenced him for good.",
        "suspects": [
            {"name": 'Station Manager Dev', "backstory": 'Constantly clashed with the host over controversial segments.', "statement": "I was reviewing tomorrow's schedule in my office. I heard nothing until the scream."},
            {"name": 'Co-Host Lily', "backstory": 'Shared the desk with the victim every night for years.', "statement": 'I left right after we went off air. He was alive, annoyed about a caller, but alive.'},
            {"name": 'Sound Engineer Max', "backstory": "Controlled the studio's live feed and door access.", "statement": 'I was in the booth cutting the final feed. The studio door was shut the whole time.'},
            {"name": 'Anonymous Caller', "backstory": 'Called in with an explosive tip just before the murder.', "statement": 'I called in about a tip, nothing more. I was never even at the station.'},
            {"name": 'Former Employee Grant', "backstory": 'Fired after the host exposed his scandal on air.', "statement": "I haven't set foot in that building since they fired me. Ask anyone."},
        ],
        "killer": 'Former Employee Grant',
        "clues": [
            'A forged visitor log entry from that night using an old employee alias',
            'The side studio door lock shows fresh pry marks',
            "A threatening voicemail left for the host, traced back to Grant's new number",
            'Security footage with a suspicious two-minute timestamp gap by the side entrance',
            'A torn employee badge, reported lost months ago, found near the studio door',
        ],
        "solution": {
            "killer_reason": 'Grant never forgave the host for exposing his scandal on air and getting him fired. He forged a visitor log entry using an old alias, pried open the side studio door, and confronted the host moments after the broadcast ended - with the microphone still live.',
            "innocent_reasons": {
                'Station Manager Dev': "Dev's office computer activity log shows continuous work at the exact time of the murder.",
                'Co-Host Lily': "Lily's car was captured on a traffic camera driving home minutes before the murder occurred.",
                'Sound Engineer Max': "Max was mid-shutdown of the live feed in the booth, visible through the booth's own window the entire time.",
                'Anonymous Caller': "Phone records confirm the anonymous caller's call came from across town, well after the murder.",
            },
        },
    },
]
