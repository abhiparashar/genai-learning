// install: npm install whatsapp-web.js qrcode-terminal sqlite3

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const sqlite3 = require('sqlite3').verbose();

// Helper: Random delay to mimic human behavior
const randomDelay = (min = 2000, max = 5000) => {
    return new Promise(resolve => 
        setTimeout(resolve, min + Math.random() * (max - min))
    );
};

// Initialize database
const db = new sqlite3.Database('whatsapp_messages.db');

db.run(`CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT,
    sender TEXT,
    message TEXT,
    timestamp INTEGER
)`);

// Initialize WhatsApp client with puppeteer args to reduce detection
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled'
        ]
    }
});

// Generate QR code for first login
client.on('qr', (qr) => {
    console.log('🔐 Scan this QR code:');
    qrcode.generate(qr, { small: true });
});

client.on('ready', async () => {
    console.log('✅ WhatsApp connected!');
    
    // Delay before starting (mimic human)
    await randomDelay(3000, 6000);
    
    // Get your group (replace with your group name)
    const chats = await client.getChats();
    
    await randomDelay(2000, 4000);
    
    const targetGroup = chats.find(chat => 
        chat.isGroup && chat.name === 'YOUR_GROUP_NAME'
    );
    
    if (!targetGroup) {
        console.log('❌ Group not found');
        client.destroy();
        return;
    }
    
    console.log(`📥 Fetching messages from: ${targetGroup.name}`);
    
    await randomDelay(3000, 5000);
    
    // Get last saved timestamp
    db.get('SELECT MAX(timestamp) as last_time FROM messages', async (err, row) => {
        const lastTimestamp = row?.last_time || 0;
        
        // Delay before fetching
        await randomDelay(2000, 4000);
        
        // Fetch messages (limit to avoid suspicion)
        const messages = await targetGroup.fetchMessages({ limit: 50 });
        
        let newCount = 0;
        
        for (const msg of messages) {
            // Only save new messages
            if (msg.timestamp > lastTimestamp) {
                // Random delay between processing each message
                await randomDelay(3000, 6000);
                
                const sender = await msg.getContact();
                
                db.run(`INSERT INTO messages (group_name, sender, message, timestamp) 
                        VALUES (?, ?, ?, ?)`,
                    [targetGroup.name, sender.pushname || sender.number, msg.body, msg.timestamp]
                );
                
                newCount++;
            }
        }
        
        console.log(`✅ Saved ${newCount} new messages`);
        
        // Final delay before logout
        await randomDelay(3000, 5000);
        
        // Close connection gracefully
        client.destroy();
        
        setTimeout(() => {
            db.close();
            process.exit(0);
        }, 2000);
    });
});

// Handle errors
client.on('auth_failure', () => {
    console.log('❌ Authentication failed');
});

client.on('disconnected', (reason) => {
    console.log('⚠️ Disconnected:', reason);
});

client.initialize();