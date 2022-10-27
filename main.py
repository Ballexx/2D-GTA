# Imports

from ursina import *
from ursina.prefabs.health_bar import HealthBar
import random, math

app = Ursina()

# Preset-Models
soundtrack = Audio("soundtrack.mp3", pitch=1, loop=True)
player = Entity(model="quad", texture="player_model", scale=(1, 1, 1))
background = Entity(model="quad", color=rgb(0, 150, 0), scale=(300, 300), z=10)
house = Entity(model="quad", color=color.black, scale=(10, 10, 10), x=20)

fuel = Entity(model="quad", texture="fuel", scale=(3, 3, 3), x=27)
ATM = Entity(model="quad", texture="ATM", scale=(3, 3, 3), x=14)
ATMmenu = Entity(
    parent=camera.ui,
    model="quad",
    scale=(0.5, 0.8),
    origin=(-0.5, 0.5),
    position=(-0.3, 0.4),
    texture="white_cube",
    texture_scale=(5, 8),
    color=color.dark_gray,
    visible=False,
)
ATMmenu.item_parent = Entity(parent=ATMmenu, scale=(1 / 5, 1 / 8))
gun_show = Entity(
    parent=camera.ui,
    model="quad",
    scale=(0.3, 0.3),
    position=(0, 0),
    visible=False,
    texture="gun_model",
)
rpg_show = Entity(
    parent=camera.ui,
    model="quad",
    scale=(0.5, 0.4),
    position=(0, 0),
    visible=False,
    texture="rpg",
    rotation_z=-40,
)

# Actions

Health = HealthBar(bar_color=color.green, roundness=0.5)
follow = SmoothFollow(target=player, speed=5, offset=[0, 0, -30])
camera.add_script(follow)

# Loaders

bullets, rpg_ammo, NPC, police_NPC, cars, grenades = [], [], [], [], [], []


def loadNPCs(civ_amount):
    for i in range(civ_amount):
        NPC.append(
            Entity(
                model="quad",
                texture="NPC_model",
                scale=(1, 1, 1),
                collider="box",
                rotation_z=random.randint(0, 360),
                z=3,
            )
        )
        NPC[i].position = (random.randint(-50, 50), random.randint(-50, 50), 0)


def loadPoliceNPCs(police_amount):
    for i in range(police_amount):
        police_NPC.append(
            Entity(
                model="quad",
                texture="police_model",
                scale=(2, 2, 2),
                collider="box",
                z=3,
                rotation_z=random.randint(0, 360),
            )
        )
        police_NPC[i].position = (random.randint(-50, 50), random.randint(-50, 50), 0)


def loadCars(car_amount):
    for i in range(car_amount):
        if i % 2 == 0:
            cars.append(
                Entity(
                    model="quad",
                    texture="car",
                    scale=(4, 4, 4),
                    collider="box",
                    z=2,
                    rotation_z=270,
                )
            )
            cars[i].position = (i * 15, 8, 0)
        else:
            cars.append(
                Entity(
                    model="quad",
                    texture="car2",
                    scale=(4, 6, 4),
                    collider="box",
                    z=2,
                    rotation_z=90,
                )
            )
            cars[i].position = (i * 15, 16, 0)


def spawnNPC(location_x, location_y):
    NPC.append(
        Entity(
            model="quad",
            texture="NPC_model",
            scale=(1, 1, 1),
            collider="box",
            rotation_z=random.randint(0, 360),
            z=3,
        )
    )
    NPC[len(NPC) - 1].position = (location_x, location_y, 0)


ammo, grenade_ammo = 16, 1
# AI-Behaviour


def NPC_behaviour(NPC, police_NPC):

    # Stop cars from driving over you

    for i in range(len(cars) - 1):
        if cars[i] != cars[current_car_id]:
            if (
                cars[i].x - player.x > 5
                or player.x - cars[i].x > 3
                or player.y - cars[i].y > 2
                or cars[i].y - player.y > 2
            ):
                cars[i].position -= cars[i].up * (time.dt / 15) * 5

    global wanted
    for i in range(len(NPC)):
        if cars[current_car_id].intersects(NPC[i]) and carMode:
            NPC[i].texture = "blood"
            NPC[i].scale = (2, 2, 1)
            NPC[i].collision = False
            wanted = True

    for bullet in range(len(bullets)):
        for i in range(len(NPC)):
            if bullets[bullet].intersects(NPC[i]):
                NPC[i].texture = "blood"
                NPC[i].scale = (2, 2, 1)
                NPC[i].collision = False
                wanted = True

    for i in range(len(police_NPC)):
        if cars[current_car_id].intersects(police_NPC[i]) and carMode:
            police_NPC[i].texture = "blood"
            police_NPC[i].scale = (2, 2, 1)
            police_NPC[i].collision = False
            wanted = True

    for bullet in range(len(bullets)):
        for i in range(len(police_NPC)):
            if bullets[bullet].intersects(police_NPC[i]):
                police_NPC[i].texture = "blood"
                police_NPC[i].scale = (2, 2, 1)
                police_NPC[i].collision = False
                wanted = True

    for i in range(len(NPC)):
        if NPC[i].scale != (2, 2, 1):
            NPC[i].position += NPC[i].up * time.dt

    # Cops chase

    if wanted:
        for i in range(len(police_NPC)):
            if police_NPC[i].scale != (2, 2, 1):
                if police_NPC[i].x > player.x:
                    police_NPC[i].x -= time.dt

                if police_NPC[i].x < player.x:
                    police_NPC[i].x += time.dt

                if police_NPC[i].y > player.y:
                    police_NPC[i].y -= time.dt

                if police_NPC[i].y < player.y:
                    police_NPC[i].y += time.dt

                if police_NPC[i].y > player.y and police_NPC[i].x > player.x:
                    police_NPC[i].rotation_z = -135
                if police_NPC[i].y < player.y and police_NPC[i].x > player.x:
                    police_NPC[i].rotation_z = -45
                if police_NPC[i].y > player.y and police_NPC[i].x < player.x:
                    police_NPC[i].rotation_z = 135
                if police_NPC[i].y < player.y and police_NPC[i].x < player.x:
                    police_NPC[i].rotation_z = 45

                if distance(police_NPC[i], player) < 10:
                    if timer % 100 == 0:
                        bullets.append(
                            Entity(
                                parent=police_NPC[i],
                                model="cube",
                                scale=0.05,
                                color=color.black,
                                collider="box",
                            )
                        )
                        Audio("gun_sound.mp3", pitch=1)
    else:
        for i in range(len(police_NPC)):
            police_NPC[i].position += police_NPC[i].up * time.dt


# Key Inputs

in_menu, carMode, wanted = False, False, False
current_car_id = 0
gun_mode, rpg_mode = True, False


def input(key):
    global carMode, rpg_mode, gun_mode

    if key == "e" and not carMode:
        global current_car_id
        for i in range(len(cars)):
            if distance(cars[i], player) < 3:
                if i != current_car_id:
                    spawnNPC(cars[i].x, cars[i].y - 3)

                carMode = True
                follow.target = cars[i]
                follow.offset = [0, 0, -100]
                player.visible = False
                current_car_id = i
                Audio("driving_car.mp3", pitch=1, loop=True)

    if key == "f" and carMode:
        carMode = False
        follow.target = player
        follow.offset = [0, 0, -30]
        player.visible = True
        player.position = (
            cars[current_car_id].position.x - 4,
            cars[current_car_id].position.y,
            cars[current_car_id].position.z,
        )

    global grenades, bullets, ammo

    if key == "left mouse down" and ammo > 0 and not carMode:
        if gun_mode:
            bullets.append(
                Entity(
                    parent=player,
                    model="cube",
                    scale=0.1,
                    color=color.black,
                    collider="box",
                )
            )
            ammo -= 1
            Audio("gun_sound.mp3", pitch=1)

        if rpg_mode:
            rpg_ammo.append(
                Entity(
                    parent=player,
                    model="quad",
                    scale=2,
                    texture="missile",
                    rotation_z=90,
                )
            )
            ammo -= 1
            Audio("launch_missile.mp3", pitch=1)

    if key == "r" and not carMode:
        if gun_mode:
            ammo = 16
        if rpg_mode:
            ammo = 1

        Audio("gun_reload.mp3", pitch=1)

    if key == "g" and not carMode:
        grenades.append(
            Entity(
                texture="grenade_model",
                parent=player,
                model="quad",
                scale=1,
                rotation_z=90,
            )
        )

    global wanted

    if key == "h" and not carMode:
        for i in range(len(NPC)):
            if distance(NPC[i], player) < 2:
                player.color = color.black
                wanted = True

    global in_menu

    if key == "e" and not carMode and distance(ATM, player) < 1.5 and not in_menu:
        ATMmenu.visible = True
        in_menu = True
        Button(
            parent=ATMmenu.item_parent,
            origin=(-0.5, 0.5),
            texture="cash",
            color="green",
            position=(0, 0),
        )

    if key == "f" and in_menu:
        ATMmenu.visible = False
        in_menu = False

    if key == "1":
        gun_show.visible = True
        ammo = 16
        gun_mode, rpg_mode = True, False
    else:
        gun_show.visible = False
    if key == "2":
        rpg_show.visible = True
        ammo = 1
        gun_mode, rpg_mode = False, True

    else:
        rpg_show.visible = False


# Gametimer

timer = 0


def update():
    player_hit_info = raycast(
        player.position,
        direction=(0, 0, 1),
        distance=inf,
        traverse_target=scene,
        ignore=list(),
        debug=False,
    )

    global timer
    timer += 1

    if not in_menu:
        NPC_behaviour(NPC, police_NPC)

        for bullet in bullets:
            bullet.y += time.dt * 50

        for rocket in rpg_ammo:
            rocket.y += time.dt * 25

            rocket_hit_info = raycast(
                rocket.position,
                direction=(0,0,1),
                distance=inf,
                traverse_target=scene,
                ignore=list(),
                debug=True,
            )
            if rocket_hit_info.hit:
                Entity(
                    model="quad",
                    color=color.red,
                    scale=(3, 3, 3),
                    position=player.position,
                )
                Audio("explosion.mp3", pitch=1)
                destroy(rocket)
                rpg_ammo.clear()

        for grenade in grenades:
            grenade.y += time.dt * 5

        if carMode:
            player.position = (
                cars[current_car_id].x,
                cars[current_car_id].y,
                cars[current_car_id].z,
            )

            for i in range(len(cars)):
                if held_keys["s"]:
                    cars[current_car_id].position -= (
                        cars[current_car_id].down * (time.dt / 15) * 2
                    )
                    cars[current_car_id].rotation_z += (
                        180 * (held_keys["a"] - held_keys["d"]) * (time.dt / 15)
                    )

                if held_keys["w"]:
                    cars[current_car_id].position -= (
                        cars[current_car_id].up * (time.dt / 15) * 5
                    )
                    cars[current_car_id].rotation_z += (
                        180 * (held_keys["d"] - held_keys["a"]) * (time.dt / 15)
                    )

        else:
            if not player_hit_info.hit:
                if held_keys["shift"]:
                    player_speed = 6
                else:
                    player_speed = 3

                player.x += held_keys["d"] * time.dt * player_speed
                player.x -= held_keys["a"] * time.dt * player_speed
                player.y += held_keys["w"] * time.dt * player_speed
                player.y -= held_keys["s"] * time.dt * player_speed

                if held_keys["s"]:
                    player.rotation_z = 180
                if held_keys["w"]:
                    player.rotation_z = 0
                if held_keys["d"]:
                    player.rotation_z = 90
                if held_keys["a"]:
                    player.rotation_z = 270
                if held_keys["w"] and held_keys["d"]:
                    player.rotation_z = 45
                if held_keys["w"] and held_keys["a"]:
                    player.rotation_z = 315
                if held_keys["a"] and held_keys["s"]:
                    player.rotation_z = 225
                if held_keys["d"] and held_keys["s"]:
                    player.rotation_z = 135
            else:
                player.position -= player.up * (time.dt / 15) * 5


# Call loaders

loadNPCs(20)
loadPoliceNPCs(10)
loadCars(20)

app.run()
