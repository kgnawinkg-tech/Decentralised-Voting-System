/**
 * evm_interactive.js
 * 
 * Implements the interaction-first physical object interface for the
 * Decentralized Blockchain Voting System.
 * 
 * - Drives 3D EVM tilt & rise from lying pose based on scroll & pointer movement.
 * - Handles physical machine buttons on the EVM Control Panel:
 *   1. REGISTER VOTER
 *   2. VOTER LOGIN
 *   3. CAST VOTE
 *   4. VERIFY RECEIPT
 *   5. ELECTION RESULTS
 *   6. HELP
 * - Handles Candidate Ballot Unit with 3D tactile blue buttons, red LED lamps,
 *   confirmation modal, atomic single-use token burn, and Web Audio beep.
 * - Handles interactive Block Inspector, Node Inspector, Merkle Node inspector,
 *   and DSA algorithm workspaces.
 */

(function () {
  'use strict';

  // --- 1. WEB AUDIO SYNTHESIZER ---
  let audioCtx = null;
  function getAudioContext() {
    if (!audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) audioCtx = new AudioContextClass();
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  }

  function playKeyClick() {
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(320, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(80, ctx.currentTime + 0.04);
      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.04);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.05);
    } catch (e) {}
  }

  function playEVMConfirmationBeep() {
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(850, ctx.currentTime); // Standard 850Hz EVM tone
      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 1.2);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 1.25);
    } catch (e) {}
  }

  // --- 2. 3D EVM SCROLL-DRIVEN TILT & POINTER PARALLAX ---
  const evmChassis = document.getElementById('physicalEVMChassis');
  const stageWrapper = document.getElementById('evmStageWrapper');

  function updateEVMScrollPose() {
    if (!evmChassis) return;
    const scrollY = window.scrollY || window.pageYOffset;
    // Initial: 50deg pitch (lying down). At 350px scroll: 0deg (upright).
    const maxScroll = 380;
    const progress = Math.min(1.0, Math.max(0, scrollY / maxScroll));
    const targetPitch = 50 * (1 - progress);
    const targetDepth = -30 * (1 - progress);
    evmChassis.style.setProperty('--evm-pitch', targetPitch.toFixed(1) + 'deg');
    evmChassis.style.setProperty('--evm-depth', targetDepth.toFixed(1) + 'px');
  }

  window.addEventListener('scroll', updateEVMScrollPose, { passive: true });
  updateEVMScrollPose();

  // Pointer perspective movement over EVM
  if (stageWrapper && evmChassis) {
    stageWrapper.addEventListener('mousemove', (e) => {
      const rect = stageWrapper.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5; // -0.5 to +0.5
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      evmChassis.style.setProperty('--evm-yaw', (x * 12).toFixed(1) + 'deg');
    });

    stageWrapper.addEventListener('mouseleave', () => {
      evmChassis.style.setProperty('--evm-yaw', '0deg');
    });
  }

  // --- 3. EVM LCD SCREEN CONTROLLER ---
  const lcdHeader = document.getElementById('evmLcdHeader');
  const lcdBody = document.getElementById('evmLcdBody');
  const ledPower = document.getElementById('ledPower');
  const ledBusy = document.getElementById('ledBusy');
  const ledVote = document.getElementById('ledVote');

  function setEVMStatus(header, bodyHtml, ledState) {
    if (lcdHeader) lcdHeader.innerText = header || 'SYSTEM READY';
    if (lcdBody) lcdBody.innerHTML = bodyHtml || '';
    if (ledPower) ledPower.className = 'evm-led-lamp green ' + (ledState.power ? 'on' : 'off');
    if (ledBusy) ledBusy.className = 'evm-led-lamp amber ' + (ledState.busy ? 'on' : 'off');
    if (ledVote) ledVote.className = 'evm-led-lamp red ' + (ledState.vote ? 'on' : 'off');
  }

  // --- 4. EVM CONTROL PANEL ACTIONS ---
  window.EVM = {
    // 1. REGISTER VOTER
    openRegister: function () {
      playKeyClick();
      setEVMStatus(
        'VOTER REGISTRATION',
        `
        <form id="evmRegisterForm" onsubmit="window.EVM.submitRegister(event)">
          <div style="display:flex; flex-direction:column; gap:0.4rem; font-size:0.8rem;">
            <input type="text" id="evmRegVoterId" placeholder="Voter ID (e.g. voter_01)" required style="background:#090e17; border:1px solid #064e3b; color:#34d399; padding:0.3rem 0.5rem; border-radius:4px; font-family:var(--font-mono);">
            <input type="text" id="evmRegName" placeholder="Full Legal Name" required style="background:#090e17; border:1px solid #064e3b; color:#34d399; padding:0.3rem 0.5rem; border-radius:4px; font-family:var(--font-mono);">
            <input type="email" id="evmRegEmail" placeholder="Email Address" required style="background:#090e17; border:1px solid #064e3b; color:#34d399; padding:0.3rem 0.5rem; border-radius:4px; font-family:var(--font-mono);">
            <input type="password" id="evmRegPwd" placeholder="Password (min 6 chars)" required style="background:#090e17; border:1px solid #064e3b; color:#34d399; padding:0.3rem 0.5rem; border-radius:4px; font-family:var(--font-mono);">
            <input type="password" id="evmRegConfirm" placeholder="Confirm Password" required style="background:#090e17; border:1px solid #064e3b; color:#34d399; padding:0.3rem 0.5rem; border-radius:4px; font-family:var(--font-mono);">
            <div style="display:flex; gap:0.5rem; margin-top:0.3rem;">
              <button type="submit" class="btn btn-primary" style="padding:0.3rem 0.6rem; font-size:0.75rem;">Submit Registration</button>
              <button type="button" class="btn btn-secondary" onclick="window.EVM.resetScreen()" style="padding:0.3rem 0.6rem; font-size:0.75rem;">Cancel</button>
            </div>
          </div>
        </form>
        `,
        { power: true, busy: true, vote: false }
      );
    },

    submitRegister: async function (e) {
      e.preventDefault();
      const voter_id = document.getElementById('evmRegVoterId').value.trim();
      const name = document.getElementById('evmRegName').value.trim();
      const email = document.getElementById('evmRegEmail').value.trim();
      const password = document.getElementById('evmRegPwd').value;
      const confirm_password = document.getElementById('evmRegConfirm').value;

      setEVMStatus('ENCRYPTING CREDENTIALS', 'Computing PBKDF2-HMAC-SHA256 salt & registering...', { power: true, busy: true, vote: false });

      try {
        const resp = await fetch('/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ voter_id, name, email, password, confirm_password })
        });
        const data = await resp.json();
        if (resp.ok && data.success) {
          playEVMConfirmationBeep();
          setEVMStatus(
            'REGISTRATION VERIFIED',
            `
            <div style="color:#34d399;">✓ Voter '${voter_id}' registered successfully!</div>
            <div style="font-size:0.78rem; margin-top:0.4rem; color:#94a3b8;">Eligible to vote in current general election.</div>
            <button type="button" class="btn btn-primary" style="margin-top:0.5rem; padding:0.3rem 0.6rem; font-size:0.75rem;" onclick="window.EVM.openLogin()">Proceed to Login &rarr;</button>
            `,
            { power: true, busy: false, vote: false }
          );
        } else {
          setEVMStatus(
            'REGISTRATION ERROR',
            `<div style="color:#f87171;">${data.message || 'Registration rejected'}</div>
             <button type="button" class="btn btn-secondary" style="margin-top:0.5rem; padding:0.3rem 0.6rem; font-size:0.75rem;" onclick="window.EVM.openRegister()">Try Again</button>`,
            { power: true, busy: false, vote: true }
          );
        }
      } catch (err) {
        setEVMStatus('COMMUNICATION ERROR', `<div style="color:#f87171;">${err.message}</div>`, { power: true, busy: false, vote: true });
      }
    },

    // 2. VOTER LOGIN
    openLogin: function () {
      playKeyClick();
      setEVMStatus(
        'VOTER AUTHENTICATION',
        `
        <form id="evmLoginForm" onsubmit="window.EVM.submitLogin(event)">
          <div style="display:flex; flex-direction:column; gap:0.5rem; font-size:0.85rem;">
            <input type="text" id="evmLoginId" placeholder="Voter ID or Email (e.g. voter_01)" required style="background:#090e17; border:1px solid #064e3b; color:#34d399; padding:0.4rem 0.6rem; border-radius:4px; font-family:var(--font-mono);">
            <input type="password" id="evmLoginPwd" placeholder="Password" required style="background:#090e17; border:1px solid #064e3b; color:#34d399; padding:0.4rem 0.6rem; border-radius:4px; font-family:var(--font-mono);">
            <div style="display:flex; gap:0.5rem; margin-top:0.4rem;">
              <button type="submit" class="btn btn-primary" style="padding:0.35rem 0.75rem; font-size:0.8rem;">Authenticate</button>
              <button type="button" class="btn btn-secondary" onclick="window.EVM.resetScreen()" style="padding:0.35rem 0.75rem; font-size:0.8rem;">Cancel</button>
            </div>
          </div>
        </form>
        `,
        { power: true, busy: true, vote: false }
      );
    },

    submitLogin: async function (e) {
      e.preventDefault();
      const identifier = document.getElementById('evmLoginId').value.trim();
      const password = document.getElementById('evmLoginPwd').value;

      setEVMStatus('VERIFYING PASSPHRASE', 'Evaluating PBKDF2 hash against salted record...', { power: true, busy: true, vote: false });

      try {
        const resp = await fetch('/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ identifier, password })
        });
        const data = await resp.json();
        if (resp.ok && data.success) {
          playKeyClick();
          window.currentVoter = data;
          setEVMStatus(
            'AUTHENTICATED',
            `
            <div style="color:#34d399;">✓ Welcome, <strong>${data.voter_name || data.voter_id}</strong>!</div>
            <div style="font-size:0.8rem; margin-top:0.4rem; color:#94a3b8;">
              Status: ${data.already_voted ? '<span style="color:#f59e0b;">ALREADY VOTED</span>' : '<span style="color:#10b981;">ELIGIBLE TO VOTE</span>'}
            </div>
            ${data.already_voted ? 
              '<p style="font-size:0.75rem; color:#f87171; margin-top:0.4rem;">You have already submitted a ballot. Single-use token was consumed.</p>' : 
              '<button type="button" class="btn btn-primary" style="margin-top:0.5rem; padding:0.35rem 0.75rem; font-size:0.8rem;" onclick="window.EVM.activateBallot()">Proceed to Cast Ballot &rarr;</button>'}
            `,
            { power: true, busy: false, vote: false }
          );
        } else {
          setEVMStatus(
            'AUTH REJECTED',
            `<div style="color:#f87171;">${data.message || 'Invalid credentials'}</div>
             <button type="button" class="btn btn-secondary" style="margin-top:0.5rem; padding:0.3rem 0.6rem; font-size:0.75rem;" onclick="window.EVM.openLogin()">Try Again</button>`,
            { power: true, busy: false, vote: true }
          );
        }
      } catch (err) {
        setEVMStatus('AUTH ERROR', `<div style="color:#f87171;">${err.message}</div>`, { power: true, busy: false, vote: true });
      }
    },

    // 3. CAST VOTE / ACTIVATE BALLOT
    activateBallot: async function () {
      playKeyClick();
      // Check auth status from server
      try {
        const resp = await fetch('/api/auth_status');
        const auth = await resp.json();
        if (!auth.authenticated) {
          setEVMStatus(
            'LOGIN REQUIRED',
            `
            <div style="color:#fbbf24;">Please log in to verify your voting eligibility.</div>
            <button type="button" class="btn btn-primary" style="margin-top:0.5rem; padding:0.35rem 0.75rem; font-size:0.8rem;" onclick="window.EVM.openLogin()">Voter Login &rarr;</button>
            `,
            { power: true, busy: false, vote: false }
          );
          return;
        }

        if (auth.already_voted) {
          setEVMStatus(
            'BALLOT CONSUMED',
            `
            <div style="color:#f87171;">You have already cast a ballot in this election.</div>
            <div style="font-size:0.78rem; margin-top:0.4rem; color:#94a3b8;">Duplicate vote attempts are blocked by cryptographic token burn.</div>
            `,
            { power: true, busy: false, vote: true }
          );
          return;
        }

        // Enable ballot unit
        setEVMStatus(
          'BALLOT ENABLED',
          `
          <div style="color:#34d399; font-weight:700;">VOTING ACTIVE FOR: ${auth.voter_name}</div>
          <div style="font-size:0.8rem; margin-top:0.35rem; color:#6ee7b7;">
            Press the 3D Blue Button beside your chosen candidate on the Ballot Unit.
          </div>
          `,
          { power: true, busy: true, vote: false }
        );
      } catch (e) {
        window.EVM.openLogin();
      }
    },

    // Candidate selection on Ballot Unit
    selectCandidate: function (candId, candName, candIndex) {
      playKeyClick();
      // Turn on candidate red lamp
      document.querySelectorAll('.evm-cand-led').forEach((led, idx) => {
        led.classList.remove('on');
        if (idx === candIndex) led.classList.add('on');
      });

      // Press button visually
      const btn = document.getElementById('candBtn_' + candId);
      if (btn) {
        btn.classList.add('pressed');
        setTimeout(() => btn.classList.remove('pressed'), 200);
      }

      // Display confirmation prompt on LCD screen
      setEVMStatus(
        'CONFIRM SELECTION',
        `
        <div>Candidate Selected: <strong style="color:#fff;">${candName}</strong></div>
        <div style="font-size:0.78rem; color:#fbbf24; margin-top:0.25rem;">
          Confirming will submit your anonymous ballot and consume your single-use token.
        </div>
        <div style="display:flex; gap:0.5rem; margin-top:0.6rem;">
          <button type="button" class="btn btn-primary" style="padding:0.35rem 0.8rem; font-size:0.8rem; background:#10b981; border-color:#059669;" onclick="window.EVM.confirmVote('${candId}', '${candName}')">
            ✓ CONFIRM VOTE
          </button>
          <button type="button" class="btn btn-secondary" style="padding:0.35rem 0.8rem; font-size:0.8rem;" onclick="window.EVM.cancelVote()">
            ✕ CANCEL
          </button>
        </div>
        `,
        { power: true, busy: true, vote: true }
      );
    },

    cancelVote: function () {
      playKeyClick();
      document.querySelectorAll('.evm-cand-led').forEach(led => led.classList.remove('on'));
      window.EVM.activateBallot();
    },

    confirmVote: async function (candId, candName) {
      setEVMStatus('TRANSMITTING BALLOT', 'Issuing blinded token & transmitting to Node A...', { power: true, busy: true, vote: false });

      try {
        const resp = await fetch('/vote', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ candidate_id: candId })
        });
        const data = await resp.json();
        if (resp.ok && data.success) {
          playEVMConfirmationBeep();
          const rcpt = data.receipt || {};
          setEVMStatus(
            'VOTE RECORDED',
            `
            <div style="color:#10b981; font-weight:700;">✓ VOTE RECORDED ON LEDGER!</div>
            <div style="font-size:0.75rem; margin-top:0.3rem; color:#94a3b8;">
              Tx Hash: <code>${(rcpt.transaction_id || '').substring(0, 16)}...</code><br>
              Block Height: #${rcpt.block_index || 1} &bull; Shard: ${rcpt.assigned_shard || 'node_a'}
            </div>
            <div style="margin-top:0.5rem; display:flex; gap:0.5rem;">
              <button type="button" class="btn btn-secondary" style="padding:0.25rem 0.5rem; font-size:0.72rem;" onclick="navigator.clipboard.writeText('${rcpt.transaction_id || ''}'); alert('Receipt ID copied!');">
                📋 Copy Receipt ID
              </button>
              <button type="button" class="btn btn-primary" style="padding:0.25rem 0.5rem; font-size:0.72rem;" onclick="window.EVM.openResults()">
                📊 View Results
              </button>
            </div>
            `,
            { power: true, busy: false, vote: true }
          );
        } else {
          setEVMStatus(
            'SUBMISSION REJECTED',
            `<div style="color:#f87171;">${data.message || 'Ballot rejected'}</div>`,
            { power: true, busy: false, vote: true }
          );
        }
      } catch (err) {
        setEVMStatus('SUBMISSION ERROR', `<div style="color:#f87171;">${err.message}</div>`, { power: true, busy: false, vote: true });
      }
    },

    // 4. VERIFY RECEIPT
    openVerify: function () {
      playKeyClick();
      setEVMStatus(
        'RECEIPT VERIFIER',
        `
        <form onsubmit="window.EVM.submitVerifyReceipt(event)">
          <div style="display:flex; flex-direction:column; gap:0.4rem; font-size:0.85rem;">
            <input type="text" id="evmVerifyReceiptId" placeholder="Paste Transaction ID / Receipt Hash" required style="background:#090e17; border:1px solid #064e3b; color:#34d399; padding:0.4rem 0.6rem; border-radius:4px; font-family:var(--font-mono); font-size:0.8rem;">
            <div style="display:flex; gap:0.5rem; margin-top:0.3rem;">
              <button type="submit" class="btn btn-primary" style="padding:0.35rem 0.75rem; font-size:0.8rem;">Verify Merkle Proof</button>
              <button type="button" class="btn btn-secondary" onclick="window.EVM.resetScreen()" style="padding:0.35rem 0.75rem; font-size:0.8rem;">Cancel</button>
            </div>
          </div>
        </form>
        `,
        { power: true, busy: true, vote: false }
      );
    },

    submitVerifyReceipt: async function (e) {
      e.preventDefault();
      const txId = document.getElementById('evmVerifyReceiptId').value.trim();
      setEVMStatus('AUDITING PROOF', 'Evaluating $O(\\log N)$ sibling hashes to Merkle root...', { power: true, busy: true, vote: false });

      try {
        const resp = await fetch(`/api/merkle_proof/${encodeURIComponent(txId)}`);
        const data = await resp.json();
        if (resp.ok && data.success) {
          playKeyClick();
          setEVMStatus(
            'RECEIPT VERIFIED',
            `
            <div style="color:#10b981; font-weight:700;">✓ INCLUSION PROOF CONFIRMED!</div>
            <div style="font-size:0.75rem; margin-top:0.3rem; color:#94a3b8;">
              Block: #${data.block_index} &bull; Proof Steps: ${data.proof ? data.proof.length : 0}<br>
              Merkle Root: <code>${(data.merkle_root || '').substring(0, 20)}...</code>
            </div>
            <button type="button" class="btn btn-secondary" style="margin-top:0.4rem; padding:0.25rem 0.5rem; font-size:0.75rem;" onclick="window.EVM.resetScreen()">Back to Ready</button>
            `,
            { power: true, busy: false, vote: false }
          );
        } else {
          setEVMStatus(
            'NOT FOUND ON CHAIN',
            `<div style="color:#fbbf24;">Transaction hash not in active ledger yet.</div>
             <button type="button" class="btn btn-secondary" style="margin-top:0.4rem; padding:0.25rem 0.5rem; font-size:0.75rem;" onclick="window.EVM.openVerify()">Try Again</button>`,
            { power: true, busy: false, vote: false }
          );
        }
      } catch (err) {
        setEVMStatus('AUDIT ERROR', `<div style="color:#f87171;">${err.message}</div>`, { power: true, busy: false, vote: true });
      }
    },

    // 5. ELECTION RESULTS
    openResults: async function () {
      playKeyClick();
      setEVMStatus('QUERYING TALLY', 'Querying certified tally from committed blocks...', { power: true, busy: true, vote: false });

      try {
        const resp = await fetch('/api/tally');
        const tally = await resp.json();
        const candHtml = (tally.candidate_results || []).map(c => 
          `<div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:0.2rem;">
            <span>${c.name}</span>
            <strong style="color:#38bdf8;">${c.votes} (${c.percentage}%)</strong>
          </div>`
        ).join('');

        setEVMStatus(
          'CERTIFIED RESULTS',
          `
          <div style="margin-bottom:0.4rem; font-size:0.75rem; color:#94a3b8;">Total Ballots: <strong style="color:#fff;">${tally.total_ballots || 0}</strong></div>
          <div style="max-height:80px; overflow-y:auto;">${candHtml}</div>
          <button type="button" class="btn btn-secondary" style="margin-top:0.4rem; padding:0.25rem 0.5rem; font-size:0.75rem;" onclick="window.EVM.resetScreen()">Close</button>
          `,
          { power: true, busy: false, vote: false }
        );
      } catch (err) {
        setEVMStatus('TALLY ERROR', `<div style="color:#f87171;">${err.message}</div>`, { power: true, busy: false, vote: true });
      }
    },

    // 6. HELP / HOW TO VOTE
    openHelp: function () {
      playKeyClick();
      setEVMStatus(
        'VOTER GUIDE',
        `
        <div style="font-size:0.78rem; line-height:1.4; color:#94a3b8;">
          1. <strong>REGISTER</strong>: Create voter profile (PBKDF2 secured).<br>
          2. <strong>LOGIN</strong>: Receive blinded single-use token.<br>
          3. <strong>CAST VOTE</strong>: Press candidate's 3D blue button & confirm.<br>
          4. <strong>RECEIPT</strong>: Audit inclusion via Merkle proof.
        </div>
        <button type="button" class="btn btn-secondary" style="margin-top:0.4rem; padding:0.25rem 0.5rem; font-size:0.75rem;" onclick="window.EVM.resetScreen()">Got It</button>
        `,
        { power: true, busy: false, vote: false }
      );
    },

    resetScreen: function () {
      playKeyClick();
      setEVMStatus(
        'STATUS: READY',
        `
        <div>BALLOT SYSTEM READY</div>
        <div style="font-size:0.8rem; color:#94a3b8; margin-top:0.3rem;">
          Select an option from the physical control buttons below.
        </div>
        `,
        { power: true, busy: false, vote: false }
      );
    }
  };

  // --- 5. INTERACTIVE OBJECT INSPECTORS ---

  // Block Inspector Drawer
  window.inspectBlock = function (blockIndex, blockHash, prevHash, merkleRoot, txCount, timestamp, isGenesis) {
    playKeyClick();
    const modal = document.getElementById('blockInspectorModal');
    if (!modal) return;
    document.getElementById('inspBlockHeight').innerText = '#' + blockIndex;
    document.getElementById('inspBlockHash').innerText = blockHash;
    document.getElementById('inspPrevHash').innerText = prevHash || '0000000000000000000000000000000000000000000000000000000000000000';
    document.getElementById('inspMerkleRoot').innerText = merkleRoot || 'N/A';
    document.getElementById('inspTxCount').innerText = txCount + ' Transactions';
    document.getElementById('inspTimestamp').innerText = new Date(timestamp * 1000).toLocaleString();
    modal.style.display = 'flex';
  };

  window.closeBlockInspector = function () {
    const modal = document.getElementById('blockInspectorModal');
    if (modal) modal.style.display = 'none';
  };

  // Node Inspector Drawer
  window.inspectNode = function (nodeId, name, endpoint, blockHeight, latency, isOnline) {
    playKeyClick();
    const modal = document.getElementById('nodeInspectorModal');
    if (!modal) return;
    document.getElementById('inspNodeName').innerText = name + ' (' + nodeId + ')';
    document.getElementById('inspNodeEndpoint').innerText = endpoint;
    document.getElementById('inspNodeHeight').innerText = '#' + blockHeight;
    document.getElementById('inspNodeLatency').innerText = latency + ' ms';
    document.getElementById('inspNodeStatus').innerText = isOnline ? 'ONLINE' : 'OFFLINE';
    document.getElementById('inspNodeStatus').className = isOnline ? 'badge badge-success' : 'badge badge-danger';
    modal.style.display = 'flex';
  };

  window.closeNodeInspector = function () {
    const modal = document.getElementById('nodeInspectorModal');
    if (modal) modal.style.display = 'none';
  };

  // Merkle Node Inspector
  window.inspectMerkleNode = function (type, hash, leftChild, rightChild) {
    playKeyClick();
    alert(`[MERKLE NODE INSPECTION]\nType: ${type.toUpperCase()}\nHash: ${hash}\nLeft: ${leftChild || 'Leaf Payload'}\nRight: ${rightChild || 'N/A'}`);
  };

  console.log('Interactive physical EVM & object-based UI initialized.');
})();
