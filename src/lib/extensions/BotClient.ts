import {
	AkairoClient,
	CommandHandler,
	InhibitorHandler,
	ListenerHandler
} from 'discord-akairo';
import { Guild } from 'discord.js';
import * as path from 'path';
import { DataTypes, Sequelize } from 'sequelize';
import * as Models from '../types/Models';
import { BotGuild } from './BotGuild';
import { BotMessage } from './BotMessage';
import { Util } from './Util';

export interface BotConfig {
	token: string;
	owners: string[];
	prefix: string;
}

export class BotClient extends AkairoClient {
	public config: BotConfig;
	public listenerHandler: ListenerHandler;
	public inhibitorHandler: InhibitorHandler;
	public commandHandler: CommandHandler;
	public util: Util;
	public ownerID: string[];
	public db: Sequelize;
	constructor(config: BotConfig) {
		super(
			{
				ownerID: config.owners
			},
			{
				allowedMentions: { parse: ['users'] } // No everyone or role mentions by default
			}
		);

		// Set token
		this.token = config.token;

		// Set config
		this.config = config;

		// Create listener handler
		this.listenerHandler = new ListenerHandler(this, {
			directory: path.join(__dirname, '..', '..', 'listeners'),
			automateCategories: true
		});

		// Create inhibitor handler
		this.inhibitorHandler = new InhibitorHandler(this, {
			directory: path.join(__dirname, '..', '..', 'inhibitors'),
			automateCategories: true
		});

		// Create command handler
		this.commandHandler = new CommandHandler(this, {
			directory: path.join(__dirname, '..', '..', 'commands'),
			prefix: async ({ guild }: { guild: Guild }) => {
				const row = await Models.Guild.findByPk(guild.id);
				if (!row) return this.config.prefix; // shouldn't be possible but you never know
				return row.prefix as string;
			},
			allowMention: true,
			handleEdits: true,
			commandUtil: true,
			commandUtilLifetime: 3e5,
			argumentDefaults: {
				prompt: {
					timeout: 'Timed out.',
					ended: 'Too many tries.',
					cancel: 'Canceled.',
					time: 3e4
				}
			},
			ignorePermissions: this.config.owners,
			ignoreCooldown: this.config.owners,
			automateCategories: true
		});

		this.util = new Util(this);
		this.db = new Sequelize({
			dialect: 'sqlite',
			storage: path.join(__dirname, '..', '..', '..', 'data.db'),
			logging: false
		});
		BotGuild.install();
		BotMessage.install();
	}

	// Initialize everything
	private async _init(): Promise<void> {
		this.commandHandler.useListenerHandler(this.listenerHandler);
		this.commandHandler.useInhibitorHandler(this.inhibitorHandler);
		this.listenerHandler.setEmitters({
			commandHandler: this.commandHandler,
			listenerHandler: this.listenerHandler,
			process
		});
		// loads all the handlers
		const loaders = {
			commands: this.commandHandler,
			listeners: this.listenerHandler,
			inhibitors: this.inhibitorHandler
		};
		for (const loader of Object.keys(loaders)) {
			try {
				loaders[loader].loadAll();
				console.log('Successfully loaded ' + loader + '.');
			} catch (e) {
				console.error('Unable to load loader ' + loader + ' with error ' + e);
			}
		}
		await this.dbPreInit();
	}

	public async dbPreInit(): Promise<void> {
		await this.db.authenticate();
		await Models.Guild.init(
			{
				id: {
					type: DataTypes.STRING,
					primaryKey: true
				},
				prefix: {
					type: DataTypes.STRING,
					allowNull: false,
					defaultValue: this.config.prefix
				}
			},
			{ sequelize: this.db }
		);

		await this.db.sync({ alter: true }); // Sync all tables to fix everything if updated
	}

	public async dbPostInit(): Promise<void> {
		for (const guild of this.guilds.cache.values()) {
			const existing = await Models.Guild.findByPk(guild.id);
			if (existing !== null) return;
			const row = Models.Guild.build({
				id: guild.id
			});
			await row.save();
		}
	}

	public async start(): Promise<void> {
		await this._init();
		await this.login(this.config.token);
	}

	public destroy(relogin = true): void | Promise<string> {
		super.destroy();
		if (relogin) {
			return this.login(this.config.token);
		}
	}
}
