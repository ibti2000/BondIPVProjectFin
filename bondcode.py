import numpy as np
from scipy.stats import norm

def bond_price(face_value, coupon_rate, periods, market_rate, m=1):


    if not float(periods * m).is_integer():
        raise ValueError("periods * m must be an integer (whole number of coupon dates).")
    n = int(periods * m)
    payment = face_value * coupon_rate / m
    I_Y = market_rate / m
    bps = 0.01 / 100
    mbps = bps / m

    #PresentValue of coupons
    discounted_coupons = sum([payment / (1 + I_Y) ** t for t in range(1, n+1)])
    #we defined in the for loop thats its incl. 1 and excl n + 1 so n mentioned
    discounted_face = face_value / (1 + I_Y) ** n # bcz only maturity
    price = discounted_coupons + discounted_face
    PVPluscoupon =  sum([payment / (1 + (I_Y + mbps)) ** t for t in range(1, n+1)])
    discounted_PVPlusface = face_value / (1 + (I_Y + mbps)) ** n # bcz only maturity
    PVPlus = PVPluscoupon + discounted_PVPlusface
    PVMinuscoupon = sum([payment / (1 + (I_Y - mbps)) ** t for t in range(1, n+1)]) 
    discounted_PVMinusface = face_value / (1 + (I_Y - mbps)) ** n # bcz only maturity 
    PVMinus = PVMinuscoupon + discounted_PVMinusface
    duration = (PVMinus - PVPlus) / (2 * price * bps)
    convexity = (PVMinus + PVPlus - (2 * price)) / (price * (bps ** 2))                          
    return price, duration, convexity

# Test 1
#price, duration, convexity = bond_price(face_value=1000, coupon_rate=0.05, periods=1, market_rate=0.05)
#print(f"Test 1 Price: {price:.2f}, Duration: {duration:.2f}, Convexity: {convexity:.2f}")

# Test 2
#price, duration, convexity = bond_price(face_value=1000, coupon_rate=0.06, periods=2, market_rate=0.05, m=2)
#print(f"Test 2 Price: {price:.2f}, Duration: {duration:.2f}, Convexity: {convexity:.2f}")

