<script>
import { useDashboard } from '../state/context'
import AgentCover from '../components/AgentCover.vue'
import { exampleBanners, exampleIcons } from './getting-started-art'
import { claudeConnectorLink, installsInHost } from '../agent-setup/data'
export default {
  components: { AgentCover },
  setup: useDashboard,
  computed: { exampleBanners: () => exampleBanners, exampleIcons: () => exampleIcons, connectorLink: () => claudeConnectorLink(location.origin), agentInHost() { return installsInHost(this.welcomeAgent) } },
  watch: { activeOrgId(){ this.pollFirstCall() } },
  mounted(){
    this.loadPlatforms()  // the catalog size in the copy
    this.pollFirstCall()
  },
  unmounted(){ this.stopFirstCallPoll() },
}
</script>

<template>

          <div class="rd-start">
            <div class="rd-welcome">
              <div class="rd-welcome-title"><span><img src="/media/redesign/welcome-mark.svg" alt=""></span><h1>Chào mừng! Bắt đầu nhanh</h1></div>
              <button v-if="canRegister" class="rd-search" @click="go('catalog'); $nextTick(()=>elements.search?.focus())"><img src="/media/redesign/search.svg" alt="">Tìm kiếm công cụ…</button>
            </div>
            <p v-if="firstTeam.name" class="rd-welcome-note">Đã tạo đội ngũ <b>{{firstTeam.name}}</b> của bạn. <a href="#orgs" @click.prevent="go('orgs')">Đổi tên</a> bất cứ lúc nào.</p>
            <p v-else-if="firstTeam.err" class="rd-welcome-note" role="alert">{{firstTeam.err}} <a href="#start" @click.prevent="autoTeam()">Thử lại</a></p>
            <div class="start-card rd-setup">
              <div class="rd-setup-side">
                <div class="start-hd">
                  <span class="start-num">1</span><b>Thiết lập cho</b>
                  <div class="rd-agent-picker" @keydown.esc.stop="startAgentOpen=false; elements.startAgentTrigger.focus()" @focusout="!$event.currentTarget.contains($event.relatedTarget) && (startAgentOpen=false)">
                    <button :ref="el => setElement('startAgentTrigger', el)" type="button" class="agent-card" :aria-expanded="startAgentOpen" aria-controls="rd-agent-options" @click="startAgentOpen=!startAgentOpen">
                      <img v-if="welcomeAgent.icon" :src="welcome.agent==='openclaw'?'/media/redesign/openclaw.svg':agentIcon(welcomeAgent.icon)" alt=""><span>{{welcomeAgent.name}}</span><span aria-hidden="true">▾</span>
                    </button>
                    <div v-if="startAgentOpen" id="rd-agent-options" class="agent-menu">
                      <button v-for="a in welcomeAgents.concat(welcomeMoreAgents)" :key="a.id" type="button" class="agent-card" :class="{on:welcome.agent===a.id}" :aria-pressed="welcome.agent===a.id" @click="welcome.agent=a.id; startAgentOpen=false; elements.startAgentTrigger.focus()"><img v-if="a.icon" :src="a.id==='openclaw'?'/media/redesign/openclaw.svg':agentIcon(a.icon)" alt=""><span>{{a.name}}</span></button>
                    </div>
                  </div>
                </div>
                <img v-if="welcome.agent==='openclaw'" class="rd-agent-preview" src="/media/redesign/openclaw-preview.png" alt="OpenClaw">
                <agent-cover v-else class="rd-agent-preview" :agent="welcome.agent" :name="welcomeAgent.name"></agent-cover>
              </div>
              <div class="start-bd rd-setup-body">
                <p class="rd-agent-context">Đang thiết lập treg cho <b>{{welcomeAgent.name}}</b></p>
                <section v-if="agentInHost" class="rd-setup-panel">
                  <p class="rd-panel-label">{{welcomeAgent.connector ? 'Thêm treg làm connector' : 'Cài đặt plugin treg'}}</p>
                  <p class="rd-token-help">Mở {{welcomeAgent.name}} và thêm treg, sau đó đăng nhập khi được yêu cầu.{{welcomeAgent.setupFallback ? '' : ' Bạn không cần cấu hình thêm câu lệnh hay API key nào.'}}</p>
                  <a v-if="welcomeAgent.connector" class="btn" :href="connectorLink" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:8px;margin:0 0 12px 16px;text-decoration:none" @click="track('onboarding_connector_add_clicked',{agent:welcome.agent,from:'start'}); startWatching || pollFirstCall()"><img :src="agentIcon(welcomeAgent.icon)" alt="" style="width:16px;height:16px">Thêm connector trong {{welcomeAgent.name}} ↗</a>
                  <a v-else class="btn" :href="welcomeAgent.plugin" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:8px;margin:0 0 12px 16px;text-decoration:none" @click="track('onboarding_plugin_install_clicked',{agent:welcome.agent,from:'start'}); startWatching || pollFirstCall()"><img :src="agentIcon(welcomeAgent.icon)" alt="" style="width:16px;height:16px">Cài plugin trong {{welcomeAgent.name}} ↗</a>
                </section>
                <template v-if="!agentInHost || welcomeAgent.setupFallback">
                <section class="rd-setup-panel">
                  <p class="rd-panel-label">{{welcomeAgent.setupFallback || "Trong khung chat của Agent, gửi:"}}</p>
                  <div class="lc-codewrap"><button class="lc-cp" @click="track('onboarding_setup_copied',{agent:welcome.agent,from:'start'}); copyStart(welcomeSetupCopy,'gsc'); startWatching || pollFirstCall()">{{startCopied==='gsc'?'Đã chép':'Sao chép'}}</button><pre style="white-space:pre-wrap;overflow-wrap:anywhere">{{welcomeSetupShown}}</pre></div>
                </section>
                <section v-if="myToken" class="rd-setup-panel">
                  <p class="rd-panel-label">Khóa API của bạn</p>
                  <p class="rd-token-help">Quá trình thiết lập sẽ tự động đăng nhập Agent. Đây là khóa Mặc định của đội ngũ (header <code>X-Treg-Token</code>). Các khóa bổ sung và khóa của Agent chỉ hiển thị một lần duy nhất; bạn có thể quản lý tại mục Đội ngũ.</p>
                  <div class="lc-codewrap rd-token-code"><div class="rd-token-actions"><button class="rd-token-toggle" @click="startTokenShow=!startTokenShow" :aria-label="startTokenShow?'Ẩn khóa':'Hiện khóa'"><img :src="'/media/redesign/'+(startTokenShow?'eye-open':'eye-closed')+'.svg'" alt=""></button><button class="lc-cp" @click="copyStart(myToken,'gsk')">{{startCopied==='gsk'?'Đã chép':'Sao chép'}}</button></div><pre>{{startTokenShow ? myToken : (myToken.slice(0,14)+'••••••••••••••••')}}</pre></div>
                </section>
                <section v-else-if="defaultKeyState==='disabled'" class="rd-setup-panel">
                  <p class="rd-panel-label">Khóa API của bạn</p>
                  <p class="rd-token-help">Khóa Mặc định của đội ngũ này đang bị vô hiệu hóa, do đó bị ẩn và không thể sử dụng.</p>
                  <button class="btn sm" @click="enableDefaultKey" :disabled="keyBusy">{{keyBusy?'…':'Bật khóa'}}</button>
                </section>
                </template>
                <section v-if="startStage" class="rd-setup-panel rd-agent-status" :class="'is-'+startStage" role="status" aria-live="polite">
                  <p class="rd-panel-label"><span class="rd-status-dot" aria-hidden="true"></span>{{startStage==='waiting' ? 'Đang chờ Agent của bạn kết nối…' : startStage==='connected' ? 'Đã kết nối' : 'Lượt gọi đầu tiên đã thực hiện' + (startProgress.first_call.tool ? ': ' + startProgress.first_call.tool : '')}}</p>
                  <p v-if="startStage==='waiting'" class="rd-token-help">{{startWatching ? 'Gửi câu lệnh thiết lập cho Agent. Trang này sẽ tự động cập nhật ngay khi Agent kết nối đến treg.' : 'Chưa có lượt kết nối nào tới treg.'}} <a v-if="!startWatching" href="#start" @click.prevent="pollFirstCall()">Kiểm tra lại</a></p>
                  <p v-else-if="startStage==='connected'" class="rd-token-help">Agent đã kết nối thành công với treg. Hãy thử gửi một prompt mẫu ở mục Thử nghiệm bên dưới.</p>
                  <p v-else class="rd-token-help">Agent của bạn đã được thiết lập và hoạt động tốt. Xem toàn bộ nhật ký cuộc gọi tại <a href="#activity" @click.prevent="go('activity')">Nhật ký hoạt động</a>.</p>
                </section>

              </div>
            </div>

          <!-- ② Try it out -->
          <div class="start-card rd-try">
            <div class="start-hd"><span class="start-num">2</span><b style="font-size:16px">Thử nghiệm ngay</b></div>
            <div class="start-bd">
              <p class="rd-try-intro">Sao chép prompt mẫu bên dưới và gửi cho Agent của bạn.</p>
              <div class="try-grid">
                <button v-for="ex in tryExamples" :key="ex.k" type="button" class="try-card" :class="['rd-task-'+ex.k, 'rd-try-art']" @click="track('tryit_prompt_copied',{key:ex.k,cat:ex.cat,from:'getting_started'}); copyStart(ex.prompt,'try-'+ex.k)">
                  <img v-if="exampleBanners[ex.k]" class="rd-try-banner" :src="exampleBanners[ex.k]" alt="" loading="lazy">
                  <span class="rd-try-panel">
                    <span class="try-cat"><span style="display:inline-flex;align-items:center;gap:7px"><img class="try-ico" :src="exampleIcons[ex.k] || '/media/redesign/try-'+({trend:'tiktok',enr:'people',serp:'google',soc:'linkedin',posts:'linkedin'}[ex.k] || 'people')+'.svg'" alt=""/>{{ex.cat}}</span><span class="try-copy" :class="{done:startCopied==='try-'+ex.k}">{{startCopied==='try-'+ex.k ? '✓ đã chép' : '⧉ sao chép'}}</span></span>
                    <span class="try-txt">{{ex.show || ex.prompt}}</span>
                  </span>
                </button>
              </div>
              <div class="oauth-div"><span>kết nối thêm tài khoản OAuth để mở khóa các năng lực mới cho Agent</span></div>
              <div v-for="g in tryOauth" :key="g.label" style="margin-top:14px">
                <div class="oauth-grp">{{g.label}}</div>
                <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">
                  <button v-for="p in g.items" :key="p.s" type="button" class="prov-chip" @click="track('tryit_oauth_clicked',{service:p.s,group:g.label,from:'getting_started'}); openProvider(p.s)"><img :src="'/media/redesign/oauth-'+({'google-business-profile':'business-profile','google-search-console':'search-console'}[p.s]||p.s)+'.svg'" alt=""/>{{p.n}}</button>
                  <span v-if="g.soon.length" class="soon-note" :data-tip="g.soon.map(p=>p.n).join(', ')">{{g.soon.length}} sắp ra mắt</span>
                </div>
              </div>
            </div>
          </div>

          <!-- BUILD ON TREG -->
          <div class="rd-build">
            <h2 style="margin:0 0 4px;font-size:17px">Phát triển trên nền tảng treg</h2>
            <p class="sub" style="margin:0 0 12px">Tùy chọn dành cho hai nhóm đối tác. Mỗi lựa chọn là một file skill — dán câu lệnh vào AI Coding Agent trong repo của bạn để tự động triển khai.</p>
            <div class="seg">
              <button :class="{on:buildTab==='vendor'}" @click="buildTab='vendor'">Niêm yết dịch vụ (Vendor)</button>
              <button :class="{on:buildTab==='platform'}" @click="buildTab='platform'">Tích hợp vào nền tảng của bạn</button>
            </div>

            <div v-show="buildTab==='vendor'" class="rd-build-panel">
              <p class="sub">Đưa API của bạn tiếp cận với hàng ngàn AI Agent trên treg. Agent của bạn sẽ tự đọc tài liệu hướng dẫn, soạn mục danh mục cho endpoint cùng giá cước và mở Pull Request.</p>
              <div class="lc-codewrap" style="margin-top:8px">
                <button class="lc-cp" @click="copyStart('Read '+proxy+'/vendor-listing.md and add our API to the treg catalog, then open a PR.','vend')">{{startCopied==='vend'?'✓ đã chép':'sao chép'}}</button>
                <pre>Read <span class="hl-str">{{proxy}}/vendor-listing.md</span> and add our API to the
treg catalog, then open a PR.</pre>
              </div>
            </div>

            <div v-show="buildTab==='platform'" class="rd-build-panel">
              <p class="sub">Cung cấp cho người dùng của <i>bạn</i> {{toolCountText||'hàng ngàn'}} công cụ mà không cần quản lý riêng từng API key — đồng thời tính phí từng khách hàng theo đúng mức sử dụng thực tế. Hỗ trợ đa dạng phương thức gọi (HTTP, MCP, CLI), gắn tag theo khách hàng, quản lý hạn mức chi tiêu và xuất hóa đơn.</p>
              <div class="lc-codewrap" style="margin-top:8px">
                <button class="lc-cp" @click="copyStart('Read '+proxy+'/integrate.md and integrate treg into our product, including per-customer usage tracking and billing.','intg')">{{startCopied==='intg'?'✓ đã chép':'sao chép'}}</button>
                <pre>Read <span class="hl-str">{{proxy}}/integrate.md</span> and integrate treg into our
product, including per-customer usage tracking and billing.</pre>
              </div>
            </div>
          </div>

          <!-- The manual CLI paths, kept but tucked away -->
          <details style="margin-top:26px" :open="startTab==='setup'">
            <summary class="sub" style="cursor:pointer;margin-bottom:0">Thích dùng Terminal? Hướng dẫn cài đặt CLI thủ công &amp; chia sẻ khóa cho đội ngũ →</summary>
            <div class="seg" style="margin-top:14px">
            <button :class="{on:startTab==='access'}" @click="startTab='access'">Truy cập 2.000+ công cụ treg</button>
            <button :class="{on:startTab==='setup'}" @click="startTab='setup'">Thiết lập công cụ của riêng bạn</button>
          </div>

          <!-- TAB · Access the catalog — agent instruction first, then the manual CLI walkthrough -->
          <div v-show="startTab==='access'" style="max-width:720px">
            <p class="sub">{{toolCountText ? toolCountText+' endpoints trong danh mục' : 'Endpoints trong danh mục'}}: SEO &amp; backlinks, mạng xã hội &amp; xu hướng, làm giàu dữ liệu cá nhân &amp; doanh nghiệp, quảng cáo. Tìm kiếm công cụ theo <i>tác vụ</i>, kiểm tra giá, gọi ngay — không cần đăng ký tài khoản ở từng nhà cung cấp. Tài khoản mới xác thực được nhận <b>$1.00 tín dụng miễn phí</b> trên đội ngũ đủ điều kiện, đủ cho hàng trăm lượt gọi.</p>

            <div class="lbl" style="margin-top:16px">▸ Thiết lập tự động với Agent <span class="muted" style="font-weight:400">— chỉ cần dán lệnh</span></div>
            <p class="sub">Một dòng lệnh duy nhất, kèm sẵn token — Agent sẽ tự đọc llms.txt và thực hiện toàn bộ: cài đặt CLI, đăng nhập và thực hiện cuộc gọi đầu tiên.</p>
            <div class="lc-codewrap" style="margin-top:8px"><button class="lc-cp" @click="copyAgentGuide('agent')">{{agentRowCopied==='agent'?'✓ đã chép':'sao chép'}}</button><pre style="max-height:240px;overflow:auto">{{buildAgentPrompt('agent', true)}}</pre></div>

            <div class="lbl" style="margin-top:26px">▸ Hoặc cài đặt thủ công</div>
            <div class="lbl" style="margin-top:14px">1 · Cài đặt CLI</div>
            <p class="sub">Cài đặt lệnh <span class="mono">treg</span> và kết nối tới máy chủ này. Cập nhật phiên bản mới sau này bằng lệnh <span class="mono">treg update</span>.</p>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart('curl -fsSL '+proxy+'/install.sh | sh','i')">{{startCopied==='i'?'✓ đã chép':'sao chép'}}</button><pre><span class="hl-cmd">curl</span> -fsSL <span class="hl-str">{{proxy}}/install.sh</span> | sh</pre></div>

            <div class="lbl" style="margin-top:22px">2 · Đăng nhập</div>
            <p class="sub">Mở trình duyệt để xác thực qua GitHub, Google hoặc mã email. Lần đăng nhập đầu tiên cũng đồng thời tạo tài khoản.</p>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart('treg login','l')">{{startCopied==='l'?'✓ đã chép':'sao chép'}}</button><pre><span class="hl-cmd">treg</span> login</pre></div>

            <div class="lbl" style="margin-top:22px">3 · Gọi thử công cụ — không cần key, không cần cài đặt</div>
            <p class="sub">Tìm kiếm trong danh mục theo tác vụ cần làm, kiểm tra giá, thực hiện gọi và theo dõi chính xác chi phí.</p>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart('treg catalog search &quot;backlinks for a domain&quot;\ntreg call tikhub.tiktok.user.profile --query uniqueId=tiktok\ntreg balance','cat1')">{{startCopied==='cat1'?'✓ đã chép':'sao chép'}}</button><pre><span class="hl-cmd">treg</span> catalog search <span class="hl-str">"backlinks for a domain"</span>
<span class="hl-cmd">treg</span> call tikhub.tiktok.user.profile <span class="hl-flag">--query</span> uniqueId=tiktok
<span class="hl-cmd">treg</span> balance      <span class="hl-comment"># xem chi tiết số dư và chi phí</span></pre></div>
          </div>

          <!-- TAB · Setup the team vault — two sections: set it up, then let the team use it -->
          <div v-show="startTab==='setup'" style="max-width:720px">
            <p class="sub">Chia sẻ skills &amp; API keys với cả đội ngũ — các khóa trong <span class="mono">.env</span> và thư mục skill trở thành công cụ mà mọi Agent của thành viên đều có thể gọi, mà khóa không bao giờ rời khỏi máy chủ.</p>

            <div class="lbl" style="margin-top:16px">▸ Thiết lập tự động với Agent <span class="muted" style="font-weight:400">— chỉ cần dán lệnh</span></div>
            <p class="sub">Một dòng lệnh duy nhất, kèm sẵn token — Agent sẽ tự đọc llms.txt, cài đặt CLI, đăng nhập và có thể đăng ký các skills + keys nội bộ làm công cụ dùng chung (quét dạng chỉ đọc trước, bạn phê duyệt).</p>
            <div class="lc-codewrap" style="margin-top:8px"><button class="lc-cp" @click="copyAgentGuide('agent')">{{agentRowCopied==='agent'?'✓ đã chép':'sao chép'}}</button><pre style="max-height:240px;overflow:auto">{{buildAgentPrompt('agent', true)}}</pre></div>

            <div class="lbl" style="margin-top:26px">▸ Hoặc cài đặt thủ công</div>
            <div class="lbl" style="margin-top:14px">1 · Cài đặt CLI</div>
            <p class="sub">Cài đặt lệnh <span class="mono">treg</span> và kết nối tới máy chủ này. Cập nhật phiên bản mới sau này bằng lệnh <span class="mono">treg update</span>.</p>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart('curl -fsSL '+proxy+'/install.sh | sh','si')">{{startCopied==='si'?'✓ đã chép':'sao chép'}}</button><pre><span class="hl-cmd">curl</span> -fsSL <span class="hl-str">{{proxy}}/install.sh</span> | sh</pre></div>

            <div class="lbl" style="margin-top:22px">2 · Đăng nhập</div>
            <p class="sub">Mở trình duyệt để xác thực qua GitHub, Google hoặc mã email. Lần đăng nhập đầu tiên cũng đồng thời tạo tài khoản.</p>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart('treg login','sl')">{{startCopied==='sl'?'✓ đã chép':'sao chép'}}</button><pre><span class="hl-cmd">treg</span> login</pre></div>

            <div class="lbl" style="margin-top:22px">3 · Tải lên khóa &amp; skills của bạn</div>
            <p class="sub">Hai cách trang bị sức mạnh cho Agent: chia sẻ toàn bộ một <b>skill</b>, hoặc đăng ký một <b>API endpoint</b> đơn lẻ. Xem trước bằng lệnh <span class="mono">treg scan</span>. Hoàn toàn an toàn khi chạy lại nhiều lần.</p>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart('treg upload                 # both .env + skills in this dir\ntreg upload env --select openai,stripe\ntreg upload skills --dir ~/.claude/skills --all      # register skill from a specific path','im')">{{startCopied==='im'?'✓ đã chép':'sao chép'}}</button><pre><span class="hl-cmd">treg</span> upload                 <span class="hl-comment"># cả .env + skills trong thư mục hiện tại</span>
<span class="hl-cmd">treg</span> upload env <span class="hl-flag">--select</span> openai,stripe
<span class="hl-cmd">treg</span> upload skills <span class="hl-flag">--dir</span> <span class="hl-str">~/.claude/skills</span> <span class="hl-flag">--all</span>      <span class="hl-comment"># đăng ký skill từ một đường dẫn cụ thể</span></pre></div>

            <div class="lbl" style="margin-top:30px">▸ Sau đó — sẵn sàng cho cả đội ngũ sử dụng</div>
            <p class="sub">Công cụ nội bộ của đội ngũ: đồng đội tải skill được chia sẻ và gọi bất kỳ API nào đã đăng ký mà không cần lưu khóa trên máy cá nhân. Những lượt gọi này không bao giờ bị tính phí đo lường.</p>

            <div class="lbl" style="margin-top:14px">4 · Sử dụng công cụ chung của đội ngũ</div>
            <p class="sub">Duyệt thư viện chia sẻ, tải một skill và gọi công cụ — thông tin xác thực luôn được bảo mật trên máy chủ, không bao giờ lộ trên máy của bạn.</p>
            <div class="lc-codewrap"><button class="lc-cp" @click="copyStart('treg skill ls\ntreg skill install seo-blog-writer                    # a teammate pulls one (or --all)\ntreg call https://api.stripe.com/v1/charges','cc')">{{startCopied==='cc'?'✓ đã chép':'sao chép'}}</button><pre><span class="hl-cmd">treg</span> skill ls
<span class="hl-cmd">treg</span> skill install seo-blog-writer
<span class="hl-cmd">treg</span> call <span class="hl-str">https://api.stripe.com/v1/charges</span></pre></div>
          </div>
          </details>

          </div>

</template>
