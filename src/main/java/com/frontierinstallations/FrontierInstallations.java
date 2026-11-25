package com.frontierinstallations;

import net.minecraft.commands.Commands;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Standalone mod: structures are supplied as data-driven worldgen resources. */
@Mod(FrontierInstallations.MOD_ID)
public final class FrontierInstallations {
    public static final String MOD_ID = "frontierinstallations";

    public FrontierInstallations() {}

    @Mod.EventBusSubscriber(modid = MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
    public static final class CommandRegistration {
        @SubscribeEvent
        public static void registerCommands(RegisterCommandsEvent event) {
            event.getDispatcher().register(Commands.literal("nearestbuilding")
                .executes(ctx -> ctx.getSource().getServer().getCommands()
                    .performPrefixedCommand(ctx.getSource(), "locate structure #frontierinstallations:all")));
            event.getDispatcher().register(Commands.literal("nearest_building")
                .executes(ctx -> ctx.getSource().getServer().getCommands()
                    .performPrefixedCommand(ctx.getSource(), "locate structure #frontierinstallations:all")));
        }
    }
}
