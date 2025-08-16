import { world, BlockLocation } from "@minecraft/server";

// Регистрация блока буровой установки
world.events.beforeItemUseOn.subscribe((eventData) => {
  const player = eventData.source;
  const item = eventData.item;
  const blockLocation = eventData.blockLocation;
  
  if (item.id === "minecraft:iron_block") {
    // Создаем буровую установку
    const dimension = player.dimension;
    
    // Устанавливаем блок буровой установки
    dimension.getBlock(blockLocation).setType("minecraft:iron_block");
    
    player.sendMessage("§aБуровая установка установлена!");
    
    // Запускаем процесс бурения
    startDrilling(dimension, blockLocation);
  }
});

// Функция бурения
function startDrilling(dimension, location) {
  const drillInterval = setInterval(() => {
    try {
      // Проверяем, что блок все еще существует
      const block = dimension.getBlock(location);
      if (block.type.id !== "minecraft:iron_block") {
        clearInterval(drillInterval);
        return;
      }
      
      // Определяем направление бурения (вниз)
      const drillLocation = new BlockLocation(
        location.x,
        location.y - 1,
        location.z
      );
      
      // Проверяем блок под установкой
      const targetBlock = dimension.getBlock(drillLocation);
      
      if (targetBlock.type.id !== "minecraft:air" && 
          targetBlock.type.id !== "minecraft:bedrock") {
        
        // Добываем ресурс
        const drops = getBlockDrops(targetBlock.type.id);
        
        // Удаляем блок
        targetBlock.setType("minecraft:air");
        
        // Выбрасываем добытые ресурсы
        drops.forEach(drop => {
          dimension.spawnItem(drop, location);
        });
        
        // Эффекты
        dimension.spawnParticle("minecraft:blockcrack", location, {
          blockType: targetBlock.type.id
        });
      }
      
    } catch (error) {
      console.warn("Ошибка в буровой установке:", error);
      clearInterval(drillInterval);
    }
  }, 2000); // Бурение каждые 2 секунды
}

// Функция получения дропа с блоков
function getBlockDrops(blockId) {
  const drops = [];
  
  switch (blockId) {
    case "minecraft:stone":
      drops.push({ id: "minecraft:cobblestone", count: 1 });
      break;
    case "minecraft:coal_ore":
      drops.push({ id: "minecraft:coal", count: 1 });
      break;
    case "minecraft:iron_ore":
      drops.push({ id: "minecraft:iron_ore", count: 1 });
      break;
    case "minecraft:gold_ore":
      drops.push({ id: "minecraft:gold_ore", count: 1 });
      break;
    case "minecraft:diamond_ore":
      drops.push({ id: "minecraft:diamond", count: 1 });
      break;
    case "minecraft:emerald_ore":
      drops.push({ id: "minecraft:emerald", count: 1 });
      break;
    case "minecraft:redstone_ore":
      drops.push({ id: "minecraft:redstone", count: 4 });
      break;
    case "minecraft:lapis_ore":
      drops.push({ id: "minecraft:lapis_lazuli", count: 4 });
      break;
    default:
      // Для других блоков просто добываем их как есть
      drops.push({ id: blockId, count: 1 });
  }
  
  return drops;
}

// Обработчик разрушения буровой установки
world.events.blockBreak.subscribe((eventData) => {
  const block = eventData.brokenBlockPermutation;
  const location = eventData.block.location;
  
  if (block.type.id === "minecraft:iron_block") {
    // Проверяем, является ли это буровой установкой
    const dimension = eventData.player.dimension;
    
    // Останавливаем все процессы бурения в этой локации
    // (в реальной реализации нужно отслеживать активные установки)
    
    eventData.player.sendMessage("§cБуровая установка разрушена!");
  }
});

console.log("§aМод 'Буровая установка' загружен!");