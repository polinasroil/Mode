import { world, system, ItemStack, DynamicPropertiesDefinition } from "@minecraft/server";

const COLLECTORS_PROP = "oc_collectors";
const SCAN_RADIUS = 3; // blocks around collector to scan
const TICKS_BETWEEN_SCANS = 100; // ~5 seconds (20 ticks = 1s)

// Map ore block -> { itemId, amount }
const ORE_DROPS = {
	"minecraft:coal_ore": { itemId: "minecraft:coal", amount: 1 },
	"minecraft:deepslate_coal_ore": { itemId: "minecraft:coal", amount: 1 },
	"minecraft:iron_ore": { itemId: "minecraft:raw_iron", amount: 1 },
	"minecraft:deepslate_iron_ore": { itemId: "minecraft:raw_iron", amount: 1 },
	"minecraft:gold_ore": { itemId: "minecraft:raw_gold", amount: 1 },
	"minecraft:deepslate_gold_ore": { itemId: "minecraft:raw_gold", amount: 1 },
	"minecraft:copper_ore": { itemId: "minecraft:raw_copper", amount: 1 },
	"minecraft:deepslate_copper_ore": { itemId: "minecraft:raw_copper", amount: 1 },
	"minecraft:redstone_ore": { itemId: "minecraft:redstone", amount: 4 },
	"minecraft:deepslate_redstone_ore": { itemId: "minecraft:redstone", amount: 4 },
	"minecraft:lapis_ore": { itemId: "minecraft:lapis_lazuli", amount: 4 },
	"minecraft:deepslate_lapis_ore": { itemId: "minecraft:lapis_lazuli", amount: 4 },
	"minecraft:diamond_ore": { itemId: "minecraft:diamond", amount: 1 },
	"minecraft:deepslate_diamond_ore": { itemId: "minecraft:diamond", amount: 1 },
	"minecraft:emerald_ore": { itemId: "minecraft:emerald", amount: 1 },
	"minecraft:deepslate_emerald_ore": { itemId: "minecraft:emerald", amount: 1 },
	"minecraft:nether_quartz_ore": { itemId: "minecraft:quartz", amount: 1 },
	"minecraft:nether_gold_ore": { itemId: "minecraft:gold_nugget", amount: 6 }
};

function posKey(p) {
	return `${p.dimensionId}:${p.x},${p.y},${p.z}`;
}

function equalPos(a, b) {
	return a.x === b.x && a.y === b.y && a.z === b.z && a.dimensionId === b.dimensionId;
}

function getDimensionById(id) {
	return world.getDimension(id);
}

function loadCollectors() {
	const stored = world.getDynamicProperty(COLLECTORS_PROP);
	if (!stored) return [];
	try {
		const arr = JSON.parse(stored);
		if (Array.isArray(arr)) return arr;
	} catch {}
	return [];
}

function saveCollectors(arr) {
	world.setDynamicProperty(COLLECTORS_PROP, JSON.stringify(arr));
}

function toggleCollectorAt(block) {
	const dimId = block.dimension.id;
	const loc = block.location;
	const target = { x: loc.x, y: loc.y, z: loc.z, dimensionId: dimId };
	const list = loadCollectors();
	const idx = list.findIndex(p => equalPos(p, target));
	if (idx >= 0) {
		list.splice(idx, 1);
		saveCollectors(list);
		return false;
	} else {
		list.push(target);
		saveCollectors(list);
		return true;
	}
}

// Register world dynamic property for collectors list
world.afterEvents.worldInitialize.subscribe(ev => {
	const def = new DynamicPropertiesDefinition();
	// Up to ~120 KB of JSON text should be plenty
	def.defineString(COLLECTORS_PROP, 120000);
	ev.propertyRegistry.registerWorldDynamicProperties(def);
	// Ensure property exists
	if (world.getDynamicProperty(COLLECTORS_PROP) === undefined) {
		world.setDynamicProperty(COLLECTORS_PROP, JSON.stringify([]));
	}
});

// Sneak + use Stick on a block to toggle it as a collector
world.beforeEvents.itemUseOn.subscribe(ev => {
	try {
		const { source, itemStack, block } = ev;
		if (!source || !itemStack || !block) return;
		if (!source.isSneaking) return;
		if (itemStack.typeId !== "minecraft:stick") return;
		const enabled = toggleCollectorAt(block);
		source.sendMessage(`§7Collector ${enabled ? "§aenabled" : "§cdisabled"} §7at §f(${block.location.x}, ${block.location.y}, ${block.location.z})`);
	} catch (e) {
		// Swallow to avoid crashing scripts in release
	}
});

function isOre(block) {
	if (!block) return false;
	return ORE_DROPS.hasOwnProperty(block.typeId);
}

function collectOneOreNear(dimension, center) {
	// scan in a small cube; stop after the first ore found to keep it lightweight
	for (let dx = -SCAN_RADIUS; dx <= SCAN_RADIUS; dx++) {
		for (let dy = -SCAN_RADIUS; dy <= SCAN_RADIUS; dy++) {
			for (let dz = -SCAN_RADIUS; dz <= SCAN_RADIUS; dz++) {
				const x = center.x + dx;
				const y = center.y + dy;
				const z = center.z + dz;
				const b = dimension.getBlock({ x, y, z });
				if (b && isOre(b)) {
					const drop = ORE_DROPS[b.typeId];
					try {
						// clear the ore
						b.setType("minecraft:air");
						// spawn item(s)
						const amount = Math.max(1, drop.amount | 0);
						const stack = new ItemStack(drop.itemId, amount);
						dimension.spawnItem(stack, {
							x: center.x + 0.5,
							y: center.y + 1,
							z: center.z + 0.5
						});
					} catch {}
					return true; // processed one
				}
			}
		}
	}
	return false;
}

// Periodic scan
system.runInterval(() => {
	try {
		const entries = loadCollectors();
		if (!entries.length) return;
		for (const p of entries) {
			const dim = getDimensionById(p.dimensionId);
			if (!dim) continue;
			const center = { x: p.x, y: p.y, z: p.z };
			// attempt to collect up to 2 ores per pass per collector
			let processed = 0;
			while (processed < 2 && collectOneOreNear(dim, center)) {
				processed++;
			}
		}
	} catch {}
}, TICKS_BETWEEN_SCANS);