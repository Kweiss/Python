my_name  = 'Kyle B. Weiss'
my_age = 29 #not a lie
my_height = 75 #inches
my_weight = 202 #lbs
my_eyes = "Blue"
my_teeth = "White"
my_hair = "A lovely shade of sandy blonde"

print "Let's talk about %s." % my_name
print "He's %d inches tall." % my_height
print "He's %d pounds of pure grissle." % my_weight
print "Yup...Pure...grissle"
print "He's got %s eyes and %s hair." % (my_eyes, my_hair)
print "His teeth are usually %s depending on the coffee intake amount." % my_teeth

#this line is tricky, try to get it exactly right
print "If I add %d, %d, and %d I get %d." % (
	my_age, my_height, my_weight, my_age + my_height + my_weight)