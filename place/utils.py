from math import cos, pi, floor
import time
def inbounds(place):
    if not place.parent: return True
    return 0 <= place.x < place.parent.width and 0 <= place.y < place.parent.height
def useful_change(_self, tag, state):
    if state:
        _self.usefulTags.append(tag)
    else:
        _self.usefulTags.remove(tag)

def to_bool(val):
    try:
        return bool(int(val))
    except:
        return val == "True"

def draw_mouth(order,draw_list,x,y,width,height,color=0x7f000000):
    size = min(width,height)
    if order <= 0 or size < 15:
        return
    elif order == 1:
        draw_list.add_polyline([[x+a*width,y+b*height] for a,b in [
            [.411,.699],
            [.470,.616],
            [.514,.596],
            [.555,.651]]], color, False, size/15)
    elif order == 2:
        draw_list.add_rect_filled(x+(.363)*width,y+(.644)*height,x+(.630)*width,y+(.699)*height, color)
    elif order == 3:
        draw_list.add_polyline([[x+a*width,y+b*height] for a,b in [
            [.4,.6],
            [.5,.7],
            [.6,.6]]], color, False, size/15)
    elif order == 4:
        draw_list.add_polyline([[x+a*width,y+b*height] for a,b in [
            [.4,.640],
            [.6,.707]]], color, False, size/15)
    elif order == 5:
        draw_list.add_circle_filled(x+(.541)*width,y+(.685)*height, size/15, color, num_segments=size//4)
    else:
        draw_list.add_rect_filled(x+(.4)*width,y+(.59)*height,x+(.6)*width,y+(.72)*height, color)

def draw_eyes(draw_list, x, y, width, height, solid, color=0x7f000000, blink_offset=0, order=-1):
    size = min(width,height)
    if size < 15:
        return
    draw_mouth(order,draw_list,x,y,width,height,color)
    if solid:
        #patrick told me (balt) the code behind blinking in dms, thanks to him <3
        if floor(((time.time())*7.12)+blink_offset)%26 == 0:
            draw_list.add_polyline([(x + (1*width)/8, y + (7*height/16)), (x + (3*width)/8, y + (7*height/16))], color, thickness=size/15)
            draw_list.add_polyline([(x + (5*width)/8, y + (7*height/16)), (x + (7*width)/8, y + (7*height/16))], color, thickness=size/15)
        else:
            draw_list.add_circle_filled(x + width/4, y + (7*height/16), size/10, color, num_segments=size//4)
            draw_list.add_circle_filled(x + width*3/4, y + (7*height/16), size/10, color, num_segments=size//4)
    else:
        draw_list.add_circle(x + width/4, y + (7*height/16), size/10, color, num_segments=size//4, thickness=size/20)
        draw_list.add_circle(x + width*3/4, y + (7*height/16), size/10, color, num_segments=size//4, thickness=size/20)

infinity_polyline = [
    (0.65, 0.65), (0.8, 0.65), (0.85, 0.5), (0.8, 0.35), (0.65, 0.35),
    (0.35, 0.65), (0.2, 0.65), (0.15, 0.5), (0.2, 0.35), (0.35, 0.35)
]
def draw_infinity(draw_list, x, y, width, height):
    draw_list.add_polyline([(x + u*width, y + v*height) for u, v in infinity_polyline], 0xffffffff, True, min(width,height)/10)

epsilon_polyline = [
    (0.7, 0.3), (0.4, 0.25), (0.3, 0.35), (0.4, 0.5), (0.6, 0.5)
]
def draw_epsilon(draw_list, x, y, width, height):
    draw_list.add_polyline([(x + u*width, y + v*height) for u, v in epsilon_polyline], 0xffffffff, False, min(width,height)/10)
    draw_list.add_polyline([(x + u*width, y + (1-v)*height) for u, v in epsilon_polyline], 0xffffffff, False, min(width,height)/10)

def half_cos(t):
    t = t % (2*pi)
    if t < pi:
        return (1 + cos(t))/2
    elif t < 1.5*pi:
        return 0
    else:
        return 1

def draw_shine(draw_list, x, y, width, height, rtl):
    t = time.perf_counter() * 2.5
    if (t + 0.5) % (2*pi) < pi + 0.5:
        if rtl:
            draw_list.add_rect_filled(x + half_cos(t)*width, y, x + half_cos(t + 0.5)*width, y + height, 0x7fffffff)
        else:
            draw_list.add_rect_filled(x + (1 - half_cos(t))*width, y, x + (1 - half_cos(t + 0.5))*width, y + height, 0x7fffffff)

# UsefulMod (Always Enabled Internal)
def draw_weight(draw_list, x, y, width, height):
    pl=0.499
    fpl=[(pl,0.5), (0.5,pl), (1-pl,0.5), (0.5,1-pl)]
    draw_list.add_polyline([(x + u*width, y + v*height) for u, v in fpl], 0x1f000000, closed=True, thickness=min(width,height)/2.5)

def draw_pin(draw_list, x, y, width, height):
    draw_list.add_poly_filled([(x + u*width, y + v*height) for u, v in [(0.25,0.25),(0.5,0.5),(0.75,0.25)]], 0x8fffffff)
special_effects = {
    0: '0:  None',
    1: '1:  Focus on this block (Challenge 38)',
    2: '2:  Right flip effect',
    3: '3:  Left flip effect',
    4: '4:  Unused',
    5: '5:  Unused',
    6: '6:  Mark Hub Intro block',
    7: '7:  Unused',
    8: '8:  Draw symbol for Inner Push / Extrude / Priority being different than the default',
    9: '9:  Leave sides open to void when floating in space',
    10: '10: Mark Hub Intro ref',
    11: '11: Don\'t show box in ASCII/grid display mode',
    12: '12: Focus camera on this block when multiple players are in the level',
    13: '13: Disable glyph drawing (Performance hack in Multi Inf. 11)'
}

floor_types = ['None','Button','PlayerButton','FastTravel','Info','DemoEnd','Break','Portal','Gallery','Show','Smile']