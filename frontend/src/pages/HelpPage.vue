<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>

          <!-- chooser -->
          <template v-if="!helpMode">
            <h1>Hướng dẫn &amp; Thực hành</h1><p class="sub">Bốn cách để làm quen và làm chủ treg - hãy chọn một phương thức.</p>
            <div class="grid" style="max-width:680px">
              <div class="card" @click="helpMode='cli'" style="cursor:pointer">
                <h3>▤ Hướng dẫn CLI</h3><p class="muted" style="font-family:var(--sans);margin:7px 0 0">Toàn bộ kho công cụ ngay từ terminal của bạn - sao chép từng lệnh và làm theo từng bước. {{tutSteps.length}} bước.</p>
              </div>
              <div class="card" @click="helpMode='dashboard'; tourI=0" style="cursor:pointer">
                <h3>▚ Tham quan Bảng điều khiển</h3><p class="muted" style="font-family:var(--sans);margin:7px 0 0">Mọi thao tác bạn có thể làm trên giao diện web, kèm hình ảnh trực quan từng bước. {{tourSteps.length}} bước.</p>
              </div>
              <div class="card" @click="helpMode='import-shell'; xtut.i=0" style="cursor:pointer">
                <h3>▞ Nhập &amp; môi trường shell</h3><p class="muted" style="font-family:var(--sans);margin:7px 0 0">Biến các lệnh CLI trên máy thành công cụ chung của đội ngũ, sau đó sử dụng trực tiếp trong sandbox bảo mật. {{(tutData.importShell||[]).length}} bước.</p>
              </div>
              <div class="card" @click="helpMode='access'; xtut.i=0" style="cursor:pointer">
                <h3>▟ Phân quyền &amp; Kiểm soát truy cập</h3><p class="muted" style="font-family:var(--sans);margin:7px 0 0">Tùy biến quyền hạn công cụ cho từng thành viên và quyền chạy CLI trên máy cá nhân. {{(tutData.access||[]).length}} bước.</p>
              </div>
            </div>
            <p v-if="onboarded" class="sub" style="margin-top:14px;font-size:12px">Đã thử xong bản demo? <a href="#" @click.prevent="resetDemo" style="color:var(--accent)">Xóa các thành viên demo →</a></p>
          </template>
          <!-- CLI tutorial -->
          <template v-else-if="helpMode==='cli'">
          <div class="tut-head">
            <div><a href="#" @click.prevent="helpMode=null" class="sub" style="display:inline-block;margin-bottom:3px">← Danh mục hướng dẫn</a><h1 style="margin:0">Hướng dẫn CLI</h1></div>
            <div class="tut-actions">
              <button class="btn sm" :class="{primary:tut.panel==='concepts'}" @click="tut.panel = tut.panel==='concepts'?null:'concepts'">Khái niệm</button>
              <button class="btn sm" :class="{primary:tut.panel==='roles'}" @click="tut.panel = tut.panel==='roles'?null:'roles'">Vai trò</button>
              <button class="btn sm" :class="{primary:tut.panel==='auth'}" @click="tut.panel = tut.panel==='auth'?null:'auth'">Xác thực</button>
              <button class="btn sm" :class="{primary:tut.panel==='skills'}" @click="tut.panel = tut.panel==='skills'?null:'skills'">Skills</button>
            </div>
          </div>
          <div v-if="tut.panel==='concepts'" class="tut-cards">
            <div class="card" v-for="c in tutData.concepts" :key="c.h"><h4 v-html="c.h"></h4><p v-html="c.p"></p></div>
          </div>
          <div v-if="tut.panel==='auth'" class="tut-cards wide">
            <div class="card" v-for="c in (tutData.auth||[])" :key="c.h"><h4 v-html="c.h"></h4><p v-html="c.p"></p></div>
          </div>
          <div v-if="tut.panel==='skills'" class="tut-cards wide">
            <div class="card" v-for="c in (tutData.skills||[])" :key="c.h"><h4 v-html="c.h"></h4><p v-html="c.p"></p></div>
          </div>
          <table v-if="tut.panel==='roles'" style="max-width:640px;margin:12px 0">
            <tr><th>Hành động</th><th v-for="c in tutData.roles.cols" :key="c">{{c}}</th></tr>
            <tr v-for="r in tutData.roles.rows" :key="r[0]"><td>{{r[0]}}</td><td v-for="(v,i) in r[1]" :key="i" :style="{color:v?'var(--green)':'var(--red)'}">{{v?'✔':'✘'}}</td></tr>
          </table>
          <div class="tut-body" v-if="tutStep">
            <nav class="tut-nav">
              <template v-for="(s,i) in tutSteps" :key="i">
                <div v-if="i===0 || s.part!==tutSteps[i-1].part" class="tut-part">{{s.part}}</div>
                <button class="tut-step" :class="{active:i===tut.i}" @click="tutGo(i)"><span class="n">{{String(i+1).padStart(2,'0')}}</span>{{s.title}}</button>
              </template>
            </nav>
            <div class="tut-main">
              <div class="crumbs">{{tutStep.part}}</div>
              <h2>{{tutStep.title}}</h2>
              <span class="persona" :class="tutStep.who">{{personaLabel(tutStep.who)}}</span>
              <div class="explain" v-html="tutStep.explain"></div>
              <div class="tut-label">Câu lệnh <button class="copy" @click="tutCopy(tutStep.cmd)">{{tutCopied?'✓ đã chép':'sao chép'}}</button></div>
              <pre class="term cmd" v-html="tutHL(tutStep.cmd,'cmd')"></pre>
              <div class="tut-label">Kết quả kỳ vọng</div>
              <pre class="term out" v-html="tutHL(tutStep.out,'out')"></pre>
              <div class="tut-notice"><b>Điểm cần lưu ý:</b> <span v-html="tutStep.notice"></span></div>
              <div class="tut-foot">
                <button class="btn sm" :disabled="tut.i===0" @click="tutGo(tut.i-1)">← Trước</button>
                <span class="pos">Bước {{tut.i+1}} trên {{tutSteps.length}}</span>
                <button class="btn sm" :disabled="tut.i===tutSteps.length-1" @click="tutGo(tut.i+1)">Tiếp →</button>
              </div>
            </div>
          </div>
          </template>
          <!-- Focused tutorials (Import & shell · Team access control) - same stepper, own step arrays -->
          <template v-else-if="helpMode==='import-shell' || helpMode==='access'">
          <div class="tut-head">
            <div><a href="#" @click.prevent="helpMode=null" class="sub" style="display:inline-block;margin-bottom:3px">← Danh mục hướng dẫn</a><h1 style="margin:0">{{xtutTitle}}</h1></div>
          </div>
          <div class="tut-body" v-if="xtutStep">
            <nav class="tut-nav">
              <template v-for="(s,i) in xtutSteps" :key="i">
                <div v-if="i===0 || s.part!==xtutSteps[i-1].part" class="tut-part">{{s.part}}</div>
                <button class="tut-step" :class="{active:i===xtut.i}" @click="xtutGo(i)"><span class="n">{{String(i+1).padStart(2,'0')}}</span>{{s.title}}</button>
              </template>
            </nav>
            <div class="tut-main">
              <div class="crumbs">{{xtutStep.part}}</div>
              <h2>{{xtutStep.title}}</h2>
              <span class="persona" :class="xtutStep.who">{{personaLabel(xtutStep.who)}}</span>
              <div class="explain" v-html="xtutStep.explain"></div>
              <div class="tut-label">Câu lệnh <button class="copy" @click="tutCopy(xtutStep.cmd)">{{tutCopied?'✓ đã chép':'sao chép'}}</button></div>
              <pre class="term cmd" v-html="tutHL(xtutStep.cmd,'cmd')"></pre>
              <div class="tut-label">Kết quả kỳ vọng</div>
              <pre class="term out" v-html="tutHL(xtutStep.out,'out')"></pre>
              <div class="tut-notice"><b>Điểm cần lưu ý:</b> <span v-html="tutStep.notice"></span></div>
              <div class="tut-foot">
                <button class="btn sm" :disabled="xtut.i===0" @click="xtutGo(xtut.i-1)">← Trước</button>
                <span class="pos">Bước {{xtut.i+1}} trên {{xtutSteps.length}}</span>
                <button class="btn sm" :disabled="xtut.i===xtutSteps.length-1" @click="xtutGo(xtut.i+1)">Tiếp →</button>
              </div>
            </div>
          </div>
          </template>
          <!-- Dashboard tour -->
          <template v-else-if="helpMode==='dashboard'">
            <div class="tut-head"><div><a href="#" @click.prevent="helpMode=null" class="sub" style="display:inline-block;margin-bottom:3px">← Danh mục hướng dẫn</a><h1 style="margin:0">Tham quan Bảng điều khiển</h1></div></div>
            <div class="tut-body" v-if="tourStep">
              <nav class="tut-nav">
                <template v-for="(s,i) in tourSteps" :key="i">
                  <div v-if="i===0 || s.part!==tourSteps[i-1].part" class="tut-part">{{s.part}}</div>
                  <button class="tut-step" :class="{active:i===tourI}" @click="tourI=i"><span class="n">{{String(i+1).padStart(2,'0')}}</span>{{s.title}}</button>
                </template>
              </nav>
              <div class="tut-main">
                <div class="crumbs">{{tourStep.part}}</div>
                <h2>{{tourStep.title}}</h2>
                <span class="persona" :class="tourStep.who">{{personaTour(tourStep.who)}}</span>
                <div class="explain" v-html="tourStep.explain"></div>
                <div class="tour-mat" :style="{background:tourMatColor(tourStep.part)}"><img :src="'/dashboard-tour/img/'+tourStep.img" :alt="tourStep.title"/></div>
                <div class="tut-notice"><b>Điểm cần lưu ý:</b> <span v-html="tourStep.notice"></span></div>
                <div class="tut-foot">
                  <button class="btn sm" :disabled="tourI===0" @click="tourI--">← Trước</button>
                  <span class="pos">Bước {{tourI+1}} trên {{tourSteps.length}}</span>
                  <button class="btn sm" :disabled="tourI===tourSteps.length-1" @click="tourI++">Tiếp →</button>
                </div>
              </div>
            </div>
          </template>

</template>
