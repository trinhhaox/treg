<script>
import { useDashboard } from '../state/context'
import { t } from '../state/i18n'

export default {
  setup: useDashboard,
  data: () => ({
    activeTab: 'cursor',
    showToken: false,
    copied: '',
  }),
  mounted() {
    if (!this.myToken && this.loadDefaultToken) {
      this.loadDefaultToken()
    }
  },
  computed: {
    t() {
      return t
    },
    mcpUrl() {
      return (this.proxy || location.origin).replace(/\/$/, '') + '/mcp'
    },
    currentToken() {
      return this.myToken || (this.activeOrg && this.activeOrg.token) || 'treg_token_placeholder'
    },
    displayToken() {
      if (this.showToken) return this.currentToken
      if (!this.currentToken || this.currentToken.length <= 12) return '••••••••••••••••'
      return this.currentToken.slice(0, 10) + '••••••••••••••••' + this.currentToken.slice(-4)
    },
    cursorConfig() {
      const cfg = {
        mcpServers: {
          treg: {
            url: this.mcpUrl,
            headers: {
              "X-Treg-Token": this.currentToken
            }
          }
        }
      }
      return JSON.stringify(cfg, null, 2)
    },
    claudeCommand() {
      return `claude mcp add --scope project treg ${this.mcpUrl} --header "X-Treg-Token: ${this.currentToken}"`
    },
    windsurfConfig() {
      const cfg = {
        mcpServers: {
          treg: {
            serverUrl: this.mcpUrl,
            headers: {
              "X-Treg-Token": this.currentToken
            }
          }
        }
      }
      return JSON.stringify(cfg, null, 2)
    },
    vscodeConfig() {
      const cfg = {
        name: "treg",
        transport: "streamable_http",
        url: this.mcpUrl,
        headers: {
          "X-Treg-Token": this.currentToken
        }
      }
      return JSON.stringify(cfg, null, 2)
    },
    pythonSnippet() {
      return `# pip install mcp httpx
import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    headers = {"X-Treg-Token": "${this.currentToken}"}
    async with streamable_http_client("${this.mcpUrl}", headers=headers) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Connected to Treg! Total tools: {len(tools.tools)}")

if __name__ == "__main__":
    asyncio.run(main())`
    }
  },
  methods: {
    async doCopy(text, tag) {
      if (this.toClipboard) {
        await this.toClipboard(text)
      } else if (navigator.clipboard) {
        await navigator.clipboard.writeText(text)
      }
      this.copied = tag
      setTimeout(() => {
        if (this.copied === tag) this.copied = ''
      }, 2500)
    },
    downloadConfig(filename, content) {
      const blob = new Blob([content], { type: 'application/json' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(link.href)
    }
  }
}
</script>

<template>
  <div class="scrim" role="dialog" aria-modal="true" @click.self="agentConnectDialog=false">
    <div class="modal mcp-modal" style="max-width:680px;width:95vw;max-height:90vh;overflow-y:auto;padding:24px">
      <!-- Header -->
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px">
        <div>
          <div style="display:flex;align-items:center;gap:8px">
            <span style="font-size:20px">⚡</span>
            <h2 style="margin:0;font-size:18px;font-family:var(--mono)">{{t('mcp.title')}}</h2>
          </div>
          <p class="sub" style="margin:6px 0 0;font-size:13px">{{t('mcp.subtitle')}}</p>
        </div>
        <button class="cls" @click="agentConnectDialog=false" aria-label="Close">✕</button>
      </div>

      <!-- Team & Token Bar -->
      <div class="mcp-token-box" style="background:var(--bg2, rgba(127,127,127,.08));border:1px solid var(--line);border-radius:8px;padding:12px;margin-bottom:18px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <div style="font-size:12px;color:var(--muted)">
            {{t('mcp.team_label')}}: <b style="color:var(--fg)">{{activeName || activeSlugNow}}</b>
          </div>
          <button class="btn sm" @click="showToken = !showToken" style="font-size:11px;padding:3px 8px">
            {{showToken ? t('mcp.hide_token') : t('mcp.show_token')}}
          </button>
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <code class="mcp-token-text" style="flex:1;background:var(--bg);border:1px solid var(--line);padding:7px 10px;border-radius:6px;font-size:12px;font-family:var(--mono);word-break:break-all">
            {{displayToken}}
          </code>
          <button class="btn sm primary" @click="doCopy(currentToken, 'token')">
            {{copied === 'token' ? t('mcp.copied') : t('mcp.copy_token')}}
          </button>
        </div>
      </div>

      <!-- Agent / Client Tabs -->
      <div class="tabs mcp-tabs" style="margin-bottom:16px;display:flex;flex-wrap:wrap;gap:4px">
        <button :class="{active: activeTab==='cursor'}" @click="activeTab='cursor'">{{t('mcp.tab_cursor')}}</button>
        <button :class="{active: activeTab==='claude'}" @click="activeTab='claude'">{{t('mcp.tab_claude')}}</button>
        <button :class="{active: activeTab==='windsurf'}" @click="activeTab='windsurf'">{{t('mcp.tab_windsurf')}}</button>
        <button :class="{active: activeTab==='vscode'}" @click="activeTab='vscode'">{{t('mcp.tab_vscode')}}</button>
        <button :class="{active: activeTab==='python'}" @click="activeTab='python'">{{t('mcp.tab_python')}}</button>
      </div>

      <!-- Tab 1: Cursor -->
      <div v-if="activeTab==='cursor'" class="mcp-content">
        <p class="sub" style="margin:0 0 8px;font-size:12px">{{t('mcp.cursor_guide')}}</p>
        <pre class="mcp-code"><code>{{cursorConfig}}</code></pre>
        <div style="display:flex;gap:8px;margin-top:10px">
          <button class="btn primary sm" @click="doCopy(cursorConfig, 'cursor')">
            {{copied === 'cursor' ? t('mcp.copied') : t('mcp.copy_config')}}
          </button>
          <button class="btn sm" @click="downloadConfig('mcp.json', cursorConfig)">
            💾 {{t('mcp.download_config')}} (.cursor/mcp.json)
          </button>
        </div>
      </div>

      <!-- Tab 2: Claude Code CLI -->
      <div v-else-if="activeTab==='claude'" class="mcp-content">
        <p class="sub" style="margin:0 0 8px;font-size:12px">{{t('mcp.claude_guide')}}</p>
        <pre class="mcp-code"><code>{{claudeCommand}}</code></pre>
        <div style="display:flex;gap:8px;margin-top:10px">
          <button class="btn primary sm" @click="doCopy(claudeCommand, 'claude')">
            {{copied === 'claude' ? t('mcp.copied') : t('mcp.copy_cmd')}}
          </button>
        </div>
        <p class="sub" style="margin:12px 0 4px;font-size:11px">Kiểm tra kết nối và danh sách công cụ trong Claude Code:</p>
        <pre class="mcp-code"><code>claude mcp list</code></pre>
      </div>

      <!-- Tab 3: Windsurf -->
      <div v-else-if="activeTab==='windsurf'" class="mcp-content">
        <p class="sub" style="margin:0 0 8px;font-size:12px">{{t('mcp.windsurf_guide')}}</p>
        <pre class="mcp-code"><code>{{windsurfConfig}}</code></pre>
        <div style="display:flex;gap:8px;margin-top:10px">
          <button class="btn primary sm" @click="doCopy(windsurfConfig, 'windsurf')">
            {{copied === 'windsurf' ? t('mcp.copied') : t('mcp.copy_config')}}
          </button>
          <button class="btn sm" @click="downloadConfig('mcp_config.json', windsurfConfig)">
            💾 {{t('mcp.download_config')}} (mcp_config.json)
          </button>
        </div>
      </div>

      <!-- Tab 4: VS Code (Roo Code / Cline) -->
      <div v-else-if="activeTab==='vscode'" class="mcp-content">
        <p class="sub" style="margin:0 0 8px;font-size:12px">{{t('mcp.vscode_guide')}}</p>
        <div style="background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:10px;margin-bottom:10px;font-size:12px">
          <div style="margin-bottom:4px"><b>Server URL (Streamable HTTP):</b> <code style="margin-left:6px">{{mcpUrl}}</code></div>
          <div><b>Header:</b> <code style="margin-left:6px">X-Treg-Token: {{currentToken}}</code></div>
        </div>
        <pre class="mcp-code"><code>{{vscodeConfig}}</code></pre>
        <div style="display:flex;gap:8px;margin-top:10px">
          <button class="btn primary sm" @click="doCopy(vscodeConfig, 'vscode')">
            {{copied === 'vscode' ? t('mcp.copied') : t('mcp.copy_config')}}
          </button>
        </div>
      </div>

      <!-- Tab 5: Python SDK -->
      <div v-else-if="activeTab==='python'" class="mcp-content">
        <p class="sub" style="margin:0 0 8px;font-size:12px">{{t('mcp.python_guide')}}</p>
        <pre class="mcp-code"><code>{{pythonSnippet}}</code></pre>
        <div style="display:flex;gap:8px;margin-top:10px">
          <button class="btn primary sm" @click="doCopy(pythonSnippet, 'python')">
            {{copied === 'python' ? t('mcp.copied') : t('mcp.copy_cmd')}}
          </button>
        </div>
      </div>

      <!-- Footer Info -->
      <div style="margin-top:20px;padding-top:12px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)">
        💡 {{t('mcp.tools_count_hint')}}
      </div>
    </div>
  </div>
</template>

<style scoped>
.mcp-code {
  background: var(--bg);
  border: 1px solid var(--line);
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.45;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  max-height: 220px;
  overflow-y: auto;
  color: var(--fg);
}
</style>

