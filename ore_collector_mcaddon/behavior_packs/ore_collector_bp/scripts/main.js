import { system, world, ItemStack } from '@minecraft/server';

const ACTIVATOR_ITEM_ID = 'minecraft:stick';
const SCAN_RADIUS = 4; // blocks around the collector
const MAX_BREAKS_PER_TICK = 3; // limit for performance
const TICKS_BETWEEN_SCANS = 20; // ~1 second (20 ticks)

const ORE_ID_SET = new Set([
	'minecraft:coal_ore', 'minecraft:deepslate_coal_ore',
	'minecraft:iron_ore', 'minecraft:deepslate_iron_ore',
	'minecraft:copper_ore', 'minecraft:deepslate_copper_ore',
	'minecraft:gold_ore', 'minecraft:deepslate_gold_ore',
	'minecraft:redstone_ore', 'minecraft:deepslate_redstone_ore',
	'minecraft:lapis_ore', 'minecraft:deepslate_lapis_ore',
	'minecraft:diamond_ore', 'minecraft:deepslate_diamond_ore',
	'minecraft:emerald_ore', 'minecraft:deepslate_emerald_ore',
	'minecraft:nether_gold_ore', 'minecraft:ancient_debris'
]);

const ORE_TO_DROP = new Map([
	['minecraft:coal_ore', 'minecraft:coal'],
	['minecraft:deepslate_coal_ore', 'minecraft:coal'],
	['minecraft:iron_ore', 'minecraft:raw_iron'],
	['minecraft:deepslate_iron_ore', 'minecraft:raw_iron'],
	['minecraft:copper_ore', 'minecraft:raw_copper'],
	['minecraft:deepslate_copper_ore', 'minecraft:raw_copper'],
	['minecraft:gold_ore', 'minecraft:raw_gold'],
	['minecraft:deepslate_gold_ore', 'minecraft:raw_gold'],
	['minecraft:redstone_ore', 'minecraft:redstone'],
	['minecraft:deepslate_redstone_ore', 'minecraft:redstone'],
	['minecraft:lapis_ore', 'minecraft:lapis_lazuli'],
	['minecraft:deepslate_lapis_ore', 'minecraft:lapis_lazuli'],
	['minecraft:diamond_ore', 'minecraft:diamond'],
	['minecraft:deepslate_diamond_ore', 'minecraft:diamond'],
	['minecraft:emerald_ore', 'minecraft:emerald'],
	['minecraft:deepslate_emerald_ore', 'minecraft:emerald'],
	['minecraft:nether_gold_ore', 'minecraft:gold_nugget'],
	['minecraft:ancient_debris', 'minecraft:ancient_debris']
]);

// key => { dimId, x, y, z }
const collectors = new Map();

function makeKey(dimId, x, y, z) {
	return `${dimId}|${x}|${y}|${z}`;
}

function isOreBlock(block) {
	return block && ORE_ID_SET.has(block.typeId);
}

function scanAndMineNear(collector) {
	const dim = world.getDimension(collector.dimId);
	if (!dim) return;

	const base = { x: collector.x, y: collector.y, z: collector.z };
	const blockAt = dim.getBlock(base);
	if (!blockAt || blockAt.typeId === 'minecraft:air') {
		collectors.delete(makeKey(collector.dimId, collector.x, collector.y, collector.z));
		return;
	}

	let broken = 0;
	for (let dx = -SCAN_RADIUS; dx <= SCAN_RADIUS && broken < MAX_BREAKS_PER_TICK; dx++) {
		for (let dy = -SCAN_RADIUS; dy <= SCAN_RADIUS && broken < MAX_BREAKS_PER_TICK; dy++) {
			for (let dz = -SCAN_RADIUS; dz <= SCAN_RADIUS && broken < MAX_BREAKS_PER_TICK; dz++) {
				if (dx === 0 && dy === 0 && dz === 0) continue;
				const p = { x: base.x + dx, y: base.y + dy, z: base.z + dz };
				const b = dim.getBlock(p);
				if (!b) continue;
				if (isOreBlock(b)) {
					const dropId = ORE_TO_DROP.get(b.typeId) ?? b.typeId;
					try {
						b.setType('minecraft:air');
						dim.spawnItem(new ItemStack(dropId, 1), base);
						broken++;
					} catch (e) {
						// ignore
					}
				}
			}
		}
	}
}

world.afterEvents.itemUseOn.subscribe((ev) => {
	const { source, itemStack, block } = ev;
	if (!source || !itemStack || !block) return;
	if (itemStack.typeId !== ACTIVATOR_ITEM_ID) return;

	const pos = block.location;
	const dimId = block.dimension.id;
	const key = makeKey(dimId, pos.x, pos.y, pos.z);

	if (collectors.has(key)) {
		collectors.delete(key);
		source.sendMessage(`§cСборщик отключён: §7${pos.x} ${pos.y} ${pos.z}`);
	} else {
		collectors.set(key, { dimId, x: pos.x, y: pos.y, z: pos.z });
		source.sendMessage(`§aСборщик включён: §7${pos.x} ${pos.y} ${pos.z}`);
	}
});

system.runInterval(() => {
	let processed = 0;
	for (const [, collector] of collectors) {
		if (processed >= 6) break; // throttle collectors per scan
		scanAndMineNear(collector);
		processed++;
	}
}, TICKS_BETWEEN_SCANS);