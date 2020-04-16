# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.utils.translation import gettext_lazy as _

# Source: https://gist.github.com/rxaviers/7360908


COMMON_EMOJIS = [
    {
        "name": _("People"),
        "emojis": [
            {
                "label": _("Thumbs Up"),
                "markdown": ":thumbsup:",
                "image": "images/emojis/thumbsup.png",
            },
            {
                "label": _("Thumbs Down"),
                "markdown": ":thumbsdown:",
                "image": "images/emojis/thumbsdown.png",
            },
            {
                "label": _("Heart"),
                "markdown": ":heart:",
                "image": "images/emojis/heart.png",
            },
            {
                "label": _("Clap"),
                "markdown": ":clap:",
                "image": "images/emojis/clap.png",
            },
            {
                "label": _("Smile"),
                "markdown": ":smile:",
                "image": "images/emojis/smile.png",
            },
            {"label": _("Joy"), "markdown": ":joy:", "image": "images/emojis/joy.png",},
            {
                "label": _("Laughing"),
                "markdown": ":laughing:",
                "image": "images/emojis/laughing.png",
            },
            {"label": _("Sob"), "markdown": ":sob:", "image": "images/emojis/sob.png",},
            {
                "label": _("Heart Eyes"),
                "markdown": ":heart_eyes:",
                "image": "images/emojis/heart_eyes.png",
            },
            {
                "label": _("Smirk"),
                "markdown": ":smirk:",
                "image": "images/emojis/smirk.png",
            },
            {
                "label": _("Blush"),
                "markdown": ":blush:",
                "image": "images/emojis/blush.png",
            },
            {
                "label": _("Confused"),
                "markdown": ":confused:",
                "image": "images/emojis/confused.png",
            },
            {
                "label": _("Disappointed"),
                "markdown": ":disappointed:",
                "image": "images/emojis/disappointed.png",
            },
            {
                "label": _("Innocent"),
                "markdown": ":innocent:",
                "image": "images/emojis/innocent.png",
            },
            {
                "label": _("Neutral Face"),
                "markdown": ":neutral_face:",
                "image": "images/emojis/neutral_face.png",
            },
            {
                "label": _("Rage"),
                "markdown": ":rage:",
                "image": "images/emojis/rage.png",
            },
            {
                "label": _("Astonished"),
                "markdown": ":astonished:",
                "image": "images/emojis/astonished.png",
            },
            {
                "label": _("Stuck Out Tongue"),
                "markdown": ":stuck_out_tongue:",
                "image": "images/emojis/stuck_out_tongue.png",
            },
            {
                "label": _("Open Mouth"),
                "markdown": ":open_mouth:",
                "image": "images/emojis/open_mouth.png",
            },
            {
                "label": _("Satisfied"),
                "markdown": ":satisfied:",
                "image": "images/emojis/satisfied.png",
            },
            {
                "label": _("Scream"),
                "markdown": ":scream:",
                "image": "images/emojis/scream.png",
            },
            {
                "label": _("Sunglasses"),
                "markdown": ":sunglasses:",
                "image": "images/emojis/sunglasses.png",
            },
            {
                "label": _("Fire"),
                "markdown": ":fire:",
                "image": "images/emojis/fire.png",
            },
            {
                "label": _("Tada"),
                "markdown": ":tada:",
                "image": "images/emojis/tada.png",
            },
            {
                "label": _("See No Evil"),
                "markdown": ":see_no_evil:",
                "image": "images/emojis/see_no_evil.png",
            },
            {
                "label": _("Point Up"),
                "markdown": ":point_up:",
                "image": "images/emojis/point_up.png",
            },
            {
                "label": _("Wave"),
                "markdown": ":wave:",
                "image": "images/emojis/wave.png",
            },
            {
                "label": _("Raised Hands"),
                "markdown": ":raised_hands:",
                "image": "images/emojis/raised_hands.png",
            },
            {
                "label": _("Pray"),
                "markdown": ":pray:",
                "image": "images/emojis/pray.png",
            },
            {
                "label": _("Metal"),
                "markdown": ":metal:",
                "image": "images/emojis/metal.png",
            },
            {
                "label": _("Alien"),
                "markdown": ":alien:",
                "image": "images/emojis/alien.png",
            },
            {
                "label": _("Angel"),
                "markdown": ":angel:",
                "image": "images/emojis/angel.png",
            },
            {
                "label": _("Mask"),
                "markdown": ":mask:",
                "image": "images/emojis/mask.png",
            },
            {
                "label": _("Poop"),
                "markdown": ":poop:",
                "image": "images/emojis/poop.png",
            },
            {
                "label": _("Skull"),
                "markdown": ":skull:",
                "image": "images/emojis/skull.png",
            },
            {"label": _("Zap"), "markdown": ":zap:", "image": "images/emojis/zap.png",},
            {"label": _("ZZZ"), "markdown": ":zzz:", "image": "images/emojis/zzz.png",},
        ],
    },
    {
        "name": _("Objects"),
        "emojis": [
            {
                "label": _("Airplane"),
                "markdown": ":airplane:",
                "image": "images/emojis/airplane.png",
            },
            {
                "label": _("Banana"),
                "markdown": ":banana:",
                "image": "images/emojis/banana.png",
            },
            {
                "label": _("Beer"),
                "markdown": ":beer:",
                "image": "images/emojis/beer.png",
            },
            {
                "label": _("Bomb"),
                "markdown": ":bomb:",
                "image": "images/emojis/bomb.png",
            },
            {
                "label": _("Birthday"),
                "markdown": ":birthday:",
                "image": "images/emojis/birthday.png",
            },
            {
                "label": _("Bulb"),
                "markdown": ":bulb:",
                "image": "images/emojis/bulb.png",
            },
            {"label": _("Bus"), "markdown": ":bus:", "image": "images/emojis/bus.png",},
            {
                "label": _("Cake"),
                "markdown": ":cake:",
                "image": "images/emojis/cake.png",
            },
            {
                "label": _("Car"),
                "markdown": ":blue_car:",
                "image": "images/emojis/car.png",
            },
            {
                "label": _("Checkered Flag"),
                "markdown": ":checkered_flag:",
                "image": "images/emojis/checkered_flag.png",
            },
            {
                "label": _("Coffee"),
                "markdown": ":coffee:",
                "image": "images/emojis/coffee.png",
            },
            {
                "label": _("Eggplant"),
                "markdown": ":eggplant:",
                "image": "images/emojis/eggplant.png",
            },
            {
                "label": _("Gift"),
                "markdown": ":gift:",
                "image": "images/emojis/gift.png",
            },
            {
                "label": _("Rocket"),
                "markdown": ":rocket:",
                "image": "images/emojis/rocket.png",
            },
            {
                "label": _("Taxi"),
                "markdown": ":taxi:",
                "image": "images/emojis/taxi.png",
            },
            {"label": _("Tea"), "markdown": ":tea:", "image": "images/emojis/tea.png",},
            {
                "label": _("Train"),
                "markdown": ":train:",
                "image": "images/emojis/train.png",
            },
            {
                "label": _("Violin"),
                "markdown": ":violin:",
                "image": "images/emojis/violin.png",
            },
            {
                "label": _("Wine Glass"),
                "markdown": ":wine_glass:",
                "image": "images/emojis/wine_glass.png",
            },
        ],
    },
    {
        "name": _("Places"),
        "emojis": [
            {"label": _("Japan"), "markdown": ":jp:", "image": "images/emojis/jp.png",},
            {"label": _("UK"), "markdown": ":gb:", "image": "images/emojis/uk.png",},
            {"label": _("USA"), "markdown": ":us:", "image": "images/emojis/us.png",},
        ],
    },
    {
        "name": _("Nature"),
        "emojis": [
            {"label": _("Cat"), "markdown": ":cat:", "image": "images/emojis/cat.png",},
            {"label": _("Dog"), "markdown": ":dog:", "image": "images/emojis/dog.png",},
            {
                "label": _("Rainbow"),
                "markdown": ":rainbow:",
                "image": "images/emojis/rainbow.png",
            },
        ],
    },
]
