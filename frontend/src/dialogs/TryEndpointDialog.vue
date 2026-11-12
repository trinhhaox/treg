<script>
import { useDashboard } from '../state/context'
import TikTokPostForm from './TikTokPostForm.vue'
export default { components: { TikTokPostForm }, setup: useDashboard }
</script>

<template>
<div class="scrim" role="dialog" aria-labelledby="try-endpoint-dialog-title" aria-modal="true" v-dialog="closeEpTry" @click.self="closeEpTry" style="place-items:stretch;justify-items:end">
      <!-- Opened from a catalog tool drawer, it stacks on top of that one: same width, and the tool it
           came from stays visible underneath (ToolDrawer's .behind), one Escape away. -->
      <div class="drawer" :class="{stack:!!drawerEp}"><div class="hd" style="padding:15px 18px;border-bottom:1px solid var(--line)"><b id="try-endpoint-dialog-title">{{isTikTokPost(epTry)?'Đăng video lên TikTok':'Thử nghiệm “'+epTry.id+'”'}}</b><button class="btn sm" @click="closeEpTry" aria-label="Đóng">✕</button></div>
        <div class="bd" style="padding:16px 18px;overflow:auto">
          <template v-if="!isTikTokPost(epTry)">
          <p class="explain"><span class="mono">{{epTry.method||'GET'}} {{epTryDisplayPath}}</span><br>{{epTry.summary}}</p>
          <p class="sub" v-if="epTryAccess" style="margin:0 0 12px">
            <template v-if="epTryAccess.tier==='anonymous'">◎ {{epTryAccess.detail||'Không cần khóa nhà cung cấp — tuyến định tuyến công khai này hoàn toàn miễn phí.'}}</template>
            <template v-else-if="epTryAccess.tier==='platform'">⚡ {{epTryAccess.detail||'Không cần khóa riêng — sử dụng khóa của hệ thống, trừ vào số dư đội ngũ.'}}</template>
            <template v-else-if="epTryAccess.tier==='tool'||epTryAccess.tier==='credential'">🔑 Chạy bằng thông tin xác thực {{epTry.provider_display||epTry.provider}} của đội ngũ — tính phí bởi nhà cung cấp, không trừ số dư hệ thống.</template>
            <template v-else-if="epTryAccess.tier==='routed'">⚡ Một lượt gọi: {{(epTryAccess.plan||[]).length}} nhà cung cấp có thể phục vụ cho đội ngũ lúc này, bắt đầu với {{provName((epTryAccess.plan||[{}])[0].provider)}}.
              <details v-if="(epTryAccess.dropped||[]).length" style="margin-top:6px"><summary style="cursor:pointer">Không sử dụng cho ví dụ này ({{epTryAccess.dropped.length}})</summary>
                <ul style="margin:6px 0 0;padding-left:18px"><li v-for="d in epTryAccess.dropped" :key="d.endpoint_id"><span class="mono">{{d.endpoint_id}}</span>: {{d.why}}</li></ul></details></template>
            <template v-else>{{epTryAccess.detail||'Chưa thể gọi từ đội ngũ này.'}}</template>
          </p>

          <div v-if="epTryShowAuthSelector" class="field auth-method-field" style="max-width:520px;margin-bottom:16px">
            <label>Phương thức xác thực</label>
            <select v-model="epTryAuthMethod" @change="loadEpTryAccess">
              <option v-for="m in epTryAuthMethods" :key="m" :value="m">{{authorizationMethodLabel(epTry.provider,m)}}</option>
            </select>
          </div>

          <div class="seg" style="margin-bottom:16px">
            <button :class="{on:epTryTab==='agent'}" @click="epTryTab='agent'">AI Agent</button>
            <button :class="{on:epTryTab==='cli'}" @click="epTryTab='cli'">CLI</button>
            <button :class="{on:epTryTab==='api'}" @click="epTryTab='api'">API</button>
            <button :class="{on:epTryTab==='manual'}" @click="epTryTab='manual'">Thủ công</button>
          </div>
          </template>

          <!-- AI AGENT — one-line setup (token embedded here only), then the prompt to run this endpoint -->
          <template v-if="epTryTab==='agent'">
            <div class="lbl">1 · Thiết lập với AI Agent</div>
            <p class="sub" style="margin:4px 0 8px">Chỉ một dòng lệnh — Agent đọc llms.txt, cài CLI và xác thực danh tính của bạn. Token &amp; đội ngũ đã được tích hợp sẵn.</p>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart(epTrySetupLine,'ep-setup')">{{startCopied==='ep-setup'?'✓ đã chép':'sao chép'}}</button><pre style="white-space:pre-wrap;word-break:break-all">{{epTrySetupLine}}</pre></div>
            <div class="lbl" style="margin-top:20px">2 · Yêu cầu AI Agent sử dụng công cụ</div>
            <p class="sub" style="margin:4px 0 8px">Dán prompt này cho Agent — Agent sẽ gọi endpoint qua Treg mà không cần lưu khóa API trên máy.</p>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart(epTryAgentUse,'ep-use')">{{startCopied==='ep-use'?'✓ đã chép':'sao chép'}}</button><pre style="white-space:pre-wrap">{{epTryAgentUse}}</pre></div>
          </template>

          <!-- CLI — install, sign in, inspect, run this exact endpoint -->
          <template v-else-if="epTryTab==='cli'">
            <div class="lbl">1 · Cài đặt CLI &amp; Đăng nhập</div>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart('curl -fsSL '+proxy+'/install.sh | sh\ntreg login','ep-cli1')">{{startCopied==='ep-cli1'?'✓ đã chép':'sao chép'}}</button><pre>curl -fsSL {{proxy}}/install.sh | sh
treg login</pre></div>
            <div class="lbl" style="margin-top:18px">2 · Xem tham số &amp; giá cước</div>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart('treg catalog get '+epTry.id,'ep-cli2')">{{startCopied==='ep-cli2'?'✓ đã chép':'sao chép'}}</button><pre>treg catalog get {{epTry.id}}</pre></div>
            <div class="lbl" style="margin-top:18px">3 · Gọi công cụ — {{epTry.id==='fishaudio.voices.list'?'BYOK hoặc nền tảng được chọn tự động ở máy chủ':(epTryAccess&&epTryAccess.tier==='anonymous'?'không cần khóa nhà cung cấp':'khóa được tự động chèn ở máy chủ')}}</div>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart(epTryCliCall,'ep-cli3')">{{startCopied==='ep-cli3'?'✓ đã chép':'sao chép'}}</button><pre style="white-space:pre-wrap;word-break:break-all">{{epTryCliCall}}</pre></div>
          </template>

          <!-- API — the raw /call/ passthrough with the token header -->
          <template v-else-if="epTryTab==='api'">
            <p v-if="epTry.id==='fishaudio.voices.list'" class="sub" style="margin:0 0 8px">Một endpoint, một token duy nhất. Máy chủ trả về danh sách giọng nói chuẩn hóa từ tài khoản Fish kết nối theo BYOK hoặc từ giọng thuộc sở hữu đội ngũ.</p>
            <p v-else class="sub" style="margin:0 0 8px">Một endpoint, một token duy nhất. {{epTryAccess&&epTryAccess.tier==='anonymous'?'Tuyến định tuyến công khai này không cần khóa.':'Treg sẽ tự động chèn thông tin xác thực ở phía máy chủ.'}} Phản hồi được chuyển tiếp nguyên bản.</p>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart(epTryCurl,'ep-api')">{{startCopied==='ep-api'?'✓ đã chép':'sao chép'}}</button><pre style="white-space:pre-wrap;word-break:break-all">{{epTryCurl}}</pre></div>
            <p class="sub" v-if="!myToken" style="margin:8px 0 0;font-size:12px"><span class="mono">$TREG_TOKEN</span> là biến mẫu — hãy thay bằng API token của bạn (sao chép ở trang Bắt đầu).</p>
          </template>

          <!-- TikTok direct post: TikTok's required post screen; opened on this tab with the tabs hidden -->
          <TikTokPostForm v-else-if="isTikTokPost(epTry)" />

          <!-- MANUAL — the live test form -->
          <template v-else>
            <!-- Not callable from here (no key connected / no treg price): don't strand the user on a
                 dead Run button — point them at the tab that DOES work. -->
            <div v-if="epTryAccess && !['anonymous','platform','tool','credential','routed'].includes(epTryAccess.tier)"
                 class="banner" style="margin:0">
              {{epTryAccess.missing_message || (mkOauth(epTry.provider) ? 'Chưa thể chạy tại đây — vui lòng kết nối '+(epTry.provider_display||epTry.provider)+' trước, sau đó bấm Chạy.' : 'Endpoint này cần khóa API. Hãy sử dụng tab AI Agent / CLI / API, hoặc mang khóa riêng của bạn.')}}
              <div style="margin-top:10px">
                <button v-if="mkOauth(epTry.provider)" class="btn sm primary" @click="openProvider(epTry.provider); closeEpTry()">{{epTryAccess.action_label||endpointConnectLabel(epTry)}}</button>
                <button v-else-if="mkKnown(epTry.provider)" class="btn sm primary" @click="goByok(epTry.provider)">🔑 Mang khóa riêng (BYOK)</button>
              </div>
            </div>
            <template v-else>
              <div class="field" v-for="p in epTryVisibleParams" :key="p.name" style="max-width:520px">
                <label class="mono" style="min-width:140px">{{p.name}} <span class="muted">({{p.location}})</span><span v-if="p.required" style="color:var(--accent)"> *</span></label>
                <input v-model="p.value" :placeholder="p.required?'bắt buộc':'tùy chọn'"/>
              </div>
              <p v-if="!epTryVisibleParams.length && (epTry.method||'GET')==='GET'" class="sub" style="margin:0 0 12px">Không có tham số — chỉ cần nhấn chạy.</p>
              <template v-if="epTryBodyType==='multipart'">
                <div class="field" v-for="p in epTryMultipart" :key="p.name" style="max-width:520px">
                  <label class="mono" style="min-width:140px">{{p.name}}<span v-if="p.required" style="color:var(--accent)"> *</span></label>
                  <input v-if="String(p.type).includes('file')" type="file" :multiple="String(p.type).startsWith('array')" @change="setEpTryFiles(p.name,$event)"/>
                  <input v-else v-model="p.value" :placeholder="p.required?'bắt buộc':'tùy chọn'"/>
                </div>
              </template>
              <div v-else-if="(epTry.method||'GET')!=='GET' && epTryBody!==''" class="field" style="max-width:520px;align-items:flex-start">
                <label style="min-width:140px">Thân yêu cầu (JSON)</label>
                <textarea v-model="epTryBody" rows="6" style="width:100%;font-family:var(--mono);font-size:12px"></textarea>
              </div>
              <button class="btn primary" :disabled="epTryBusy" @click="runEpTry">{{epTryBusy ? 'Đang chạy…' : '❯ Chạy thử'}}</button>
            </template>
            <div v-if="epTryResp" style="margin-top:14px">
              <div class="muted" style="font-size:12px;margin-bottom:6px">Kết quả
                <span class="badge" :class="epTryStatus>=200&&epTryStatus<300?'ok':'invalid'">{{epTryStatus}}</span>
                · {{epTryMs}}ms<span v-if="epTryCost!=null"> · tính phí {{money(epTryCost)}}<span v-if="epTryCost===0 && epTryStatus>=200 && epTryStatus<300" :title="epTryAccess&&epTryAccess.tier==='anonymous'?'Tuyến công khai không dùng khóa và không tính phí số dư đội ngũ.':'Nhà cung cấp tính phí 0 cho lượt gọi này (ví dụ dữ liệu từ bộ nhớ đệm).'"> {{epTryAccess&&epTryAccess.tier==='anonymous'?'(miễn phí — không cần khóa ⓘ)':'(miễn phí — nhà cung cấp tính 0đ ⓘ)'}}</span></span>
                <template v-if="epTry.id!=='fishaudio.voices.list'"> · được lưu vào Hoạt động</template></div>
              <audio v-if="epTryAudioUrl" :src="epTryAudioUrl" controls style="width:100%;margin:8px 0"></audio>
              <a v-if="epTryAudioUrl" class="btn sm" :href="epTryAudioUrl" :download="epTryAudioName">Tải âm thanh về</a>
              <pre v-if="!epTryAudioUrl" style="max-height:340px;overflow:auto">{{epTryResp}}</pre>
            </div>
            <div v-if="epTry.provider==='fishaudio'" style="margin-top:20px;border-top:1px solid var(--line);padding-top:14px">
              <div style="display:flex;justify-content:space-between;align-items:center"><b>{{fishVoicesSource==='byok'?'Giọng Fish Audio của bạn':'Giọng chung đội ngũ'}}</b><button class="btn sm" @click="loadFishVoices">Làm mới</button></div>
              <p v-if="fishVoiceNote" class="sub" style="margin:6px 0 0">{{fishVoiceNote}}</p>
              <p v-if="!fishVoices.length && !fishVoiceBusy" class="sub">{{fishVoicesSource==='byok'?'Chưa có giọng nào trong tài khoản Fish Audio này.':'Chưa có giọng nào được tạo trong đội ngũ này.'}}</p>
              <p v-if="fishVoiceBusy" class="sub">Đang tải danh sách giọng nói…</p>
              <div v-for="v in fishVoices" :key="v.id" class="card" style="padding:10px;margin-top:8px">
                <div><b>{{v.display_name||'Giọng chưa đặt tên'}}</b><div class="mono muted" style="font-size:11px">{{v.upstream_id}}</div></div>
                <div style="display:flex;gap:6px;margin-top:8px;flex-wrap:wrap">
                  <button class="btn sm" @click="useFishVoice(v)">Dùng trong TTS</button>
                  <button class="btn sm" @click="beginRenameFishVoice(v)">Đổi tên</button>
                  <button class="btn sm danger" @click="beginDeleteFishVoice(v)">Xóa</button>
                </div>
              </div>
            </div>
          </template>
        </div></div>
    </div>
</template>
