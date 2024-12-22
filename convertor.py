def actionConvert(action: dict) -> str:
	res = None

	if action['type'] == 'Solid':
		res = 'new RGBActionSolid(56, {}, {}),\n'
		res = res.format(action['colors'], action['lengthy'])
	elif action['type'] == 'Fading':
		res = 'new RGBActionFading(56, {}, {}, {}),\n'
		res = res.format(action['colors'], action['section'], action['interval'])
	elif action['type'] == 'Cycle':
		res = 'new RGBActionCycle(56, {}, {}, {}, {}),\n'
		res = res.format(action['colors'], action['interval'], action['times'], action['isUp'])
	elif action['type'] == 'Floating':
		res = 'new RGBActionFloating(56, {}, {}, {}),\n'
		res = res.format(action['colors'], action['interval'], action['isUp'])
	elif action['type'] == 'Growing':
		res = 'new RGBActionGrowing(56, {}, {}, {}),\n'
		res = res.format(action['colors'], action['interval'], action['isUp'])		
	else:
		raise ValueError('Unknown action type: {}'.format(action['type']))
	
	res = res.replace('[', '{').replace(']', '}')
	res = res.replace('\'', '"')
	res = res.replace('True', 'true').replace('False', 'false')
	
	return res

def actionsConvert(actions: list) -> str:
	res = ''
	for action in actions:
		res += actionConvert(action)
	return res
