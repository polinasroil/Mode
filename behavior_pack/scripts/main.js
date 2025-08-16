// Ore Collector Mod для Minecraft PE
// Автоматический сборщик руды

// Функция для поиска руды в радиусе
function findOresInRadius(position, radius = 5) {
  const ores = [];
  const oreTypes = [
    "minecraft:coal_ore",
    "minecraft:iron_ore", 
    "minecraft:gold_ore",
    "minecraft:diamond_ore",
    "minecraft:emerald_ore",
    "minecraft:lapis_ore",
    "minecraft:redstone_ore",
    "minecraft:copper_ore",
    "minecraft:deepslate_coal_ore",
    "minecraft:deepslate_iron_ore",
    "minecraft:deepslate_gold_ore",
    "minecraft:deepslate_diamond_ore",
    "minecraft:deepslate_emerald_ore",
    "minecraft:deepslate_lapis_ore",
    "minecraft:deepslate_redstone_ore",
    "minecraft:deepslate_copper_ore"
  ];

  for (let x = -radius; x <= radius; x++) {
    for (let y = -radius; y <= radius; y++) {
      for (let z = -radius; z <= radius; z++) {
        const checkPos = { x: position.x + x, y: position.y + y, z: position.z + z };
        
        // Проверяем блок в позиции
        const block = world.getDimension("overworld").getBlock(checkPos);
        if (oreTypes.includes(block.id)) {
          ores.push({
            position: checkPos,
            type: block.id
          });
        }
      }
    }
  }
  
  return ores;
}

// Функция для сбора руды
function collectOre(oreData) {
  const dimension = world.getDimension("overworld");
  const block = dimension.getBlock(oreData.position);
  
  if (block) {
    // Заменяем руду на камень
    block.setType("minecraft:stone");
    
    // Создаем предмет руды
    const oreItem = oreData.type.replace("_ore", "");
    dimension.spawnItem({
      item: { id: `minecraft:${oreItem}` },
      location: oreData.position
    });
  }
}

// Обработчик размещения блока
world.beforeEvents.playerPlaceBlock.subscribe((eventData) => {
  const { block, player } = eventData;
  
  if (block.id === "ore_collector:ore_collector") {
    // Запускаем автоматический сбор каждые 10 секунд
    const interval = setInterval(() => {
      const ores = findOresInRadius(block.location, 5);
      
      if (ores.length > 0) {
        ores.forEach(ore => {
          collectOre(ore);
        });
        
        // Уведомляем игрока
        player.sendMessage(`§aСборщик руды нашел и собрал ${ores.length} руд!`);
      }
    }, 10000); // 10 секунд
    
    // Останавливаем интервал при разрушении блока
    world.beforeEvents.playerDestroyBlock.subscribe((destroyEvent) => {
      if (destroyEvent.block.location.x === block.location.x &&
          destroyEvent.block.location.y === block.location.y &&
          destroyEvent.block.location.z === block.location.z) {
        clearInterval(interval);
      }
    });
  }
});

// Обработчик разрушения блока
world.beforeEvents.playerDestroyBlock.subscribe((eventData) => {
  const { block } = eventData;
  
  if (block.id === "ore_collector:ore_collector") {
    // Дополнительная логика при разрушении
    eventData.player.sendMessage("§cСборщик руды разрушен!");
  }
});

// Инициализация мода
console.log("§aOre Collector Mod загружен!");