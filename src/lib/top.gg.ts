import { Webhook as TopGGWebhook, Api } from '@top-gg/sdk';
import { BotStats, WebhookPayload } from '@top-gg/sdk/dist/typings';
import { BotClient } from './extensions/BotClient';
import { topGGPort, credentials, channels } from '../config/options';
import express, { Request as ExpressRequest, Express } from 'express';
import { TextChannel, MessageEmbed, Webhook } from 'discord.js';
import { stripIndent } from 'common-tags';

interface Request extends ExpressRequest {
	vote: WebhookPayload;
}

export class TopGGHandler {
	public api: Api;
	public webhook: TopGGWebhook;
	public client: BotClient;
	public server: Express;
	public constructor(client: BotClient) {
		this.client = client;
		this.api = new Api(credentials.dblToken);
		this.webhook = new TopGGWebhook(credentials.dblWebhookAuth);
		this.server = express();
	}
	public init(): void {
		setInterval(this.postGuilds, 60000);
		this.server.post('/dblwebhook', this.webhook.middleware(), async (req) => {
			const vote = (req as Request).vote;
			await this.postVoteWebhook(vote);
		});
		this.server.listen(topGGPort);
	}
	public async postGuilds(): Promise<BotStats> {
		return await this.api.postStats({
			serverCount: this.client.guilds.cache.size,
			shardCount: this.client.shard.count
		});
	}
	public async postVoteWebhook(data: WebhookPayload): Promise<void> {
		try {
			if (data.type === 'test') {
				const channel = (await this.client.channels.fetch(
					channels.log
				)) as TextChannel;
				await channel.send(
					`Test vote webhook data recieved, ${this.client.util.haste(
						JSON.stringify(data, null, '\t')
					)}`
				);
				return;
			}
			const timestamp = new Date().getTime();
			const parsedData = {
				user: await this.client.users.fetch(data.user),
				type: data.type as 'upvote' | 'test',
				isWeekend: data.isWeekend
			};
			const channel = (await this.client.channels.fetch(
				channels.dblVote
			)) as TextChannel;
			const webhooks = await channel.fetchWebhooks();
			let webhook: Webhook;
			if (webhooks.size < 1) webhook = webhooks.first();
			else webhook = await channel.createWebhook('Utilibot Voting');
			await webhook.send(
				new MessageEmbed({
					title: 'Top.gg vote',
					description: stripIndent`
					User: ${parsedData.user.tag}
					Weekend (worth double): ${parsedData.isWeekend ? 'Yes' : 'No'}
				`,
					author: {
						name: parsedData.user.tag,
						icon_url: parsedData.user.avatarURL({ dynamic: true })
					},
					timestamp
				}),
				{
					username: 'Utilibot Voting',
					avatarURL: this.client.user.avatarURL({ dynamic: true })
				}
			);
		} catch (e) {
			console.error(e);
		}
	}
}
