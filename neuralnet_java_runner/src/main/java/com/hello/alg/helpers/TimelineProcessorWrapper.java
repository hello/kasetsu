package com.hello.alg.helpers;

import com.codahale.metrics.MetricRegistry;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.common.base.Optional;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableSet;
import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import com.google.common.collect.Sets;
import com.google.protobuf.InvalidProtocolBufferException;
import com.hello.alg.api.TimelineSensorDataProtos;
import com.hello.alg.model.TimelineProcessorOutput;
import com.hello.suripu.core.ObjectGraphRoot;
import com.hello.suripu.core.algorithmintegration.AlgorithmConfiguration;
import com.hello.suripu.core.algorithmintegration.NeuralNetEndpoint;
import com.hello.suripu.core.db.AccountReadDAO;
import com.hello.suripu.core.db.CalibrationDAO;
import com.hello.suripu.core.db.DefaultModelEnsembleDAO;
import com.hello.suripu.core.db.DeviceDataReadAllSensorsDAO;
import com.hello.suripu.core.db.DeviceReadDAO;
import com.hello.suripu.core.db.FeatureExtractionModelsDAO;
import com.hello.suripu.core.db.FeedbackReadDAO;
import com.hello.suripu.core.db.HistoricalPairingDAO;
import com.hello.suripu.core.db.OnlineHmmModelsDAO;
import com.hello.suripu.core.db.PairingDAO;
import com.hello.suripu.core.db.PillDataReadDAO;
import com.hello.suripu.core.db.RingTimeHistoryReadDAO;
import com.hello.suripu.core.db.SenseDataDAODynamoDB;
import com.hello.suripu.core.db.SleepHmmDAO;
import com.hello.suripu.core.db.SleepScoreParametersDAO;
import com.hello.suripu.core.db.SleepStatsDAO;
import com.hello.suripu.core.db.TimeZoneHistoryDAO;
import com.hello.suripu.core.db.UserTimelineTestGroupDAO;
import com.hello.suripu.core.db.colors.SenseColorDAO;
import com.hello.suripu.core.models.Account;
import com.hello.suripu.core.models.AggregateSleepStats;
import com.hello.suripu.core.models.AllSensorSampleList;
import com.hello.suripu.core.models.Calibration;
import com.hello.suripu.core.models.Device;
import com.hello.suripu.core.models.DeviceAccountPair;
import com.hello.suripu.core.models.Event;
import com.hello.suripu.core.models.OnlineHmmData;
import com.hello.suripu.core.models.OnlineHmmPriors;
import com.hello.suripu.core.models.OnlineHmmScratchPad;
import com.hello.suripu.core.models.RingTime;
import com.hello.suripu.core.models.Sample;
import com.hello.suripu.core.models.Sensor;
import com.hello.suripu.core.models.SleepScore;
import com.hello.suripu.core.models.SleepScoreParameters;
import com.hello.suripu.core.models.SleepSegment;
import com.hello.suripu.core.models.SleepStats;
import com.hello.suripu.core.models.TimeZoneHistory;
import com.hello.suripu.core.models.TimelineFeedback;
import com.hello.suripu.core.models.TimelineResult;
import com.hello.suripu.core.models.TrackerMotion;
import com.hello.suripu.core.models.device.v2.Sense;
import com.hello.suripu.core.util.DateTimeUtil;
import com.hello.suripu.core.util.FeatureExtractionModelData;
import com.hello.suripu.core.util.SleepHmmWithInterpretation;
import com.hello.suripu.coredropwizard.timeline.InstrumentedTimelineProcessor;
import com.librato.rollout.RolloutAdapter;
import com.librato.rollout.RolloutClient;
import dagger.Module;
import dagger.Provides;
import org.apache.commons.codec.binary.Base64;
import org.joda.time.DateTime;
import org.joda.time.DateTimeConstants;
import org.skife.jdbi.v2.sqlobject.Bind;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.inject.Singleton;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Created by benjo on 12/12/16.
 */


public class TimelineProcessorWrapper {

    private static final Logger LOGGER = LoggerFactory.getLogger(TimelineProcessorWrapper.class);

    private final NeuralNetEndpoint neuralNetEndpoint;
    private final InstrumentedTimelineProcessor timelineProcessor;

    private AllSensorSampleList allSensorSampleList = new AllSensorSampleList();
    private List<TrackerMotion> myMotions = Lists.newArrayList();
    private List<TrackerMotion> partnerMotions = Lists.newArrayList();
    private Long currentAccountId = 0L;
    private DateTime currentTargetDate = null;
    private List<Event> feedbackEvents = Lists.newArrayList();
    private SleepScore sleepScoreResult = null;
    private SleepStats sleepStatsResult = null;
    private Integer tzOffset;

    private static final ImmutableSet<Event.Type> SLEEP_EVENT_TYPES;

    static {
        final Set<Event.Type> eventSet = Sets.newHashSet();
        eventSet.add(Event.Type.IN_BED);
        eventSet.add(Event.Type.SLEEP);
        eventSet.add(Event.Type.WAKE_UP);
        eventSet.add(Event.Type.OUT_OF_BED);

        SLEEP_EVENT_TYPES = ImmutableSet.copyOf(eventSet);
    }

    final public PillDataReadDAO pillDataReadDAO = new PillDataReadDAO() {
        @Override
        public ImmutableList<TrackerMotion> getBetweenLocalUTC(long accountId, DateTime startLocalTime, DateTime endLocalTime) {
            if (accountId == currentAccountId) {
                return ImmutableList.copyOf(myMotions);
            }

            return ImmutableList.copyOf(partnerMotions);
        }
    };


    final private DeviceDataReadAllSensorsDAO deviceDataReadAllSensorsDAO = new DeviceDataReadAllSensorsDAO() {
        @Override
        public AllSensorSampleList generateTimeSeriesByUTCTimeAllSensors(
                Long queryStartTimestampInUTC, Long queryEndTimestampInUTC, Long accountId, String externalDeviceId,
                int slotDurationInMinutes, Integer missingDataDefaultValue, com.google.common.base.Optional<Device.Color> color,
                com.google.common.base.Optional<Calibration> calibrationOptional, final Boolean useAudioPeakEnergy) {

            return allSensorSampleList;
        }

        @Override
        public Optional<String> getSensePairedBetween(Long accountId, DateTime startTime, DateTime endTime) {
            return Optional.absent();
        }
    };

    final private RingTimeHistoryReadDAO ringTimeHistoryDAODynamoDB = new RingTimeHistoryReadDAO() {
        @Override
        public List<RingTime> getRingTimesBetween(String senseId, Long accountId, DateTime startTime, DateTime endTime) {

           return Lists.<RingTime>newArrayList();
        }
    };

    final private FeedbackReadDAO feedbackDAO = new FeedbackReadDAO() {
        @Override
        public ImmutableList<TimelineFeedback> getCorrectedForNight(Long accountId, DateTime dateOfNight) {
            return ImmutableList.copyOf(Lists.<TimelineFeedback>newArrayList());
        }

        @Override
        public ImmutableList<TimelineFeedback> getForTimeRange(Long tstartUTC, Long tstopUTC) {
            return ImmutableList.copyOf(Lists.<TimelineFeedback>newArrayList());
        }
    };

    final private SleepHmmDAO sleepHmmDAO = new SleepHmmDAO() {
        @Override
        public com.google.common.base.Optional<SleepHmmWithInterpretation> getLatestModelForDate(long accountId, long timeOfInterestMillis) {
            return com.google.common.base.Optional.absent();
        }
    };

    final private AccountReadDAO accountDAO = new AccountReadDAO() {
        @Override
        public com.google.common.base.Optional<Account> getById(Long id) {
            final Account account = new Account.Builder().withDOB("1980-01-01").build();
            return com.google.common.base.Optional.of(account);
        }

        @Override
        public com.google.common.base.Optional<Account> getByEmail(String email) {
            return null;
        }

        @Override
        public List<Account> getRecent(Integer limit) {
            return null;
        }

        @Override
        public com.google.common.base.Optional<Account> exists(String email, String password) {
            return null;
        }

        @Override
        public List<Account> getByNamePartial(String namePartial) {
            return null;
        }

        @Override
        public List<Account> getByEmailPartial(String emailPartial) {
            return null;
        }
    };


    final private SleepStatsDAO sleepStatsDAO = new SleepStatsDAO() {
        @Override
        public Boolean updateStat(Long accountId, DateTime date, Integer overallSleepScore, SleepScore sleepScore, SleepStats stats, Integer offsetMillis) {
            sleepScoreResult = sleepScore;
            sleepStatsResult = stats;
            return Boolean.TRUE;
        }

        @Override
        public com.google.common.base.Optional<Integer> getTimeZoneOffset(Long accountId) {
            return null;
        }

        @Override
        public com.google.common.base.Optional<Integer> getTimeZoneOffset(Long accountId, DateTime queryDate) {
            return null;
        }

        @Override
        public com.google.common.base.Optional<AggregateSleepStats> getSingleStat(Long accountId, String date) {
            return null;
        }

        @Override
        public ImmutableList<AggregateSleepStats> getBatchStats(Long accountId, String startDate, String endDate) {
            return null;
        }
    };

    final private TimeZoneHistoryDAO timeZoneHistoryDAO= new TimeZoneHistoryDAO(){
        @Override
        public Optional<TimeZoneHistory> updateTimeZone(final long accountId, final DateTime updatedTime, final String clientTimeZoneId, int clientTimeZoneOffsetMillis){
            return null;
        }
        @Override
        public List<TimeZoneHistory> getMostRecentTimeZoneHistory(final long accountId, final DateTime start, final int limit){
            return Collections.emptyList();
        }
        @Override
        public List<TimeZoneHistory> getTimeZoneHistory(final long accountId, final DateTime start){
            return Lists.newArrayList(new TimeZoneHistory(0L,tzOffset,"foobars"));
        }
        @Override
        public List<TimeZoneHistory> getTimeZoneHistory(final long accountId, final DateTime start, final DateTime end){
            return Lists.newArrayList(new TimeZoneHistory(0L,tzOffset,"foobars"));
        }
        @Override
        public  List<TimeZoneHistory> getTimeZoneHistory(final long accountId, final DateTime start, final DateTime end, int limit){
            return Lists.newArrayList(new TimeZoneHistory(0L,tzOffset,"foobars"));
        }
        @Override
        public Optional<TimeZoneHistory> getCurrentTimeZone(final long accountId){
            return null;
        }
        @Override
        public Map<DateTime, TimeZoneHistory> getAllTimeZones(final long accountId){
            return null;
        }

    };

    final private SenseColorDAO senseColorDAO = new SenseColorDAO() {
        @Override
        public com.google.common.base.Optional<Device.Color> getColorForSense(String senseId) {
            return com.google.common.base.Optional.absent();
        }

        @Override
        public com.google.common.base.Optional<Sense.Color> get(String senseId) {
            return null;
        }

        @Override
        public int saveColorForSense(String senseId, String color) {
            return 0;
        }

        @Override
        public int update(String senseId, String color) {
            return 0;
        }

        @Override
        public ImmutableList<String> missing() {
            return null;
        }
    };

    final private OnlineHmmModelsDAO priorsDAO = new OnlineHmmModelsDAO() {
        @Override
        public OnlineHmmData getModelDataByAccountId(Long accountId, DateTime date) {
            return null;
        }

        @Override
        public boolean updateModelPriorsAndZeroOutScratchpad(Long accountId, DateTime date, OnlineHmmPriors priors) {
            return false;
        }

        @Override
        public boolean updateScratchpad(Long accountId, DateTime date, OnlineHmmScratchPad scratchPad) {
            return false;
        }
    };

    final private FeatureExtractionModelsDAO featureExtractionModelsDAO = new FeatureExtractionModelsDAO() {
        @Override
        public FeatureExtractionModelData getLatestModelForDate(Long accountId, DateTime dateTimeLocalUTC, com.google.common.base.Optional<UUID> uuidForLogger) {
            return null;
        }
    };

    final private CalibrationDAO calibrationDAO = new CalibrationDAO() {
        @Override
        public com.google.common.base.Optional<Calibration> get(String senseId) {
            return null;
        }

        @Override
        public com.google.common.base.Optional<Calibration> getStrict(String senseId) {
            return null;
        }

        @Override
        public com.google.common.base.Optional<Boolean> putForce(Calibration calibration) {
            return null;
        }

        @Override
        public com.google.common.base.Optional<Boolean> put(Calibration calibration) {
            return null;
        }

        @Override
        public Map<String, Calibration> getBatch(Set<String> senseIds) {
            return null;
        }

        @Override
        public Map<String, Calibration> getBatchStrict(Set<String> senseIds) {
            return null;
        }

        @Override
        public Boolean delete(String senseId) {
            return null;
        }

        @Override
        public Map<String, com.google.common.base.Optional<Boolean>> putBatchForce(List<Calibration> calibrations) {
            return null;
        }

        @Override
        public Map<String, com.google.common.base.Optional<Boolean>> putBatch(List<Calibration> calibration) {
            return null;
        }
    };

    final private DefaultModelEnsembleDAO defaultModelEnsembleDAO = new DefaultModelEnsembleDAO() {
        @Override
        public OnlineHmmPriors getDefaultModelEnsemble() {
            return OnlineHmmPriors.createEmpty();
        }

        @Override
        public OnlineHmmPriors getSeedModel() {
            return OnlineHmmPriors.createEmpty();
        }
    };

    final private UserTimelineTestGroupDAO userTimelineTestGroupDAO = new UserTimelineTestGroupDAO() {
        @Override
        public com.google.common.base.Optional<Long> getUserGestGroup(Long accountId, DateTime timeToQueryUTC) {
            return com.google.common.base.Optional.absent();
        }

        @Override
        public void setUserTestGroup(Long accountId, Long groupId) {

        }
    };

    final private MetricRegistry metric = new MetricRegistry();

    /*
    final DeviceReadDAO deviceReadForTimelineDAO = new DeviceReadForTimelineDAO() {
        @Override
        public ImmutableList<DeviceAccountPair> getSensesForAccountId(Long accountId) {
            return null;
        }

        @Override
        public Optional<DeviceAccountPair> getMostRecentSensePairByAccountId(Long accountId) {
            return Optional.of(new DeviceAccountPair(0L,0L,"foobars",new DateTime(0L)));
        }

        @Override
        public Optional<Long> getPartnerAccountId(Long accountId) {
            return Optional.absent();
        }
    };
    */

    final private DeviceReadDAO deviceReadDAO = new DeviceReadDAO() {
        @Override
        public com.google.common.base.Optional<Long> getDeviceForAccountId(@Bind("account_id") Long accountId, @Bind("device_id") String deviceName) {
            return null;
        }

        @Override
        public ImmutableList<DeviceAccountPair> getSensesForAccountId(@Bind("account_id") Long accountId) {
            return ImmutableList.copyOf(Collections.EMPTY_LIST);
        }

        @Override
        public com.google.common.base.Optional<Long> getMostRecentSenseByAccountId(@Bind("account_id") Long accountId) {
            return null;
        }

        @Override
        public com.google.common.base.Optional<DeviceAccountPair> getMostRecentSensePairByAccountId(@Bind("account_id") Long accountId) {
            return com.google.common.base.Optional.of(new DeviceAccountPair(0L,0L,"foobars",new DateTime(0L)));
        }

        @Override
        public ImmutableList<DeviceAccountPair> getAccountIdsForDeviceId(@Bind("device_name") String deviceName) {
            return null;
        }

        @Override
        public com.google.common.base.Optional<Long> getIdForAccountIdDeviceId(@Bind("account_id") Long accountId, @Bind("device_name") String deviceName) {
            return null;
        }

        @Override
        public com.google.common.base.Optional<Long> getPartnerAccountId(@Bind("account_id") Long accountId) {
            return com.google.common.base.Optional.absent();
        }

        @Override
        public ImmutableList<DeviceAccountPair> getPillsForAccountId(@Bind("account_id") Long accountId) {
            return ImmutableList.copyOf(Collections.EMPTY_LIST);
        }

        @Override
        public ImmutableList<DeviceAccountPair> getLinkedAccountFromPillId(@Bind("pill_id") String deviceId) {
            return ImmutableList.copyOf(Collections.EMPTY_LIST);
        }

        @Override
        public ImmutableList<DeviceAccountPair> getAllPills(@Bind("is_active") Boolean isActive) {
            return null;
        }

        @Override
        public com.google.common.base.Optional<DeviceAccountPair> getInternalPillId(@Bind("pill_id") String pillId) {
            return null;
        }
    };

    final private AlgorithmConfiguration algorithmConfiguration = new AlgorithmConfiguration() {
        @Override
        public int getArtificalLightStartMinuteOfDay() {
            return 21*60 + 30;
        }

        @Override
        public int getArtificalLightStopMinuteOfDay() {
            return 5*60;
        }
    };

    final private SleepScoreParametersDAO sleepScoreParametersDAO = new SleepScoreParametersDAO() {

        @Override
        public SleepScoreParameters getSleepScoreParametersByDate(Long accountId, DateTime nightDate) {
            return new SleepScoreParameters(accountId, nightDate, 480);
        }

        @Override
        public Boolean upsertSleepScoreParameters(Long accountId, SleepScoreParameters parameters) {
            return null;
        }
    };


    public void clear() {
    }
    public final Map<String,Boolean> features = Maps.newHashMap();

    public void setFeature(final String feat,boolean on) {
        if (features.containsKey(feat) && !on) {
            features.remove(feat);
        }

        if (on) {
            features.put(feat,true);
        }
    }

    final private RolloutAdapter rolloutAdapter = new RolloutAdapter() {


        @Override
        public boolean userFeatureActive(String feature, long userId, List<String> userGroups) {
            Boolean hasFeature = features.get(feature);
            //System.out.print(String.format("FEATURE: %s\n",feature));
            if (hasFeature == null) {
                hasFeature = Boolean.FALSE;
            }

            LOGGER.info("userFeatureActive {}={}",feature,hasFeature);
            return hasFeature;
        }

        @Override
        public boolean deviceFeatureActive(String feature, String deviceId, List<String> userGroups) {
            Boolean hasFeature = features.get(feature);

            if (hasFeature == null) {
                hasFeature = Boolean.FALSE;
            }

            LOGGER.info("deviceFeatureActive {}={}",feature,hasFeature);
            return hasFeature;
        }
    };


    @Module(injects = InstrumentedTimelineProcessor.class, library = true)
    public class RolloutLocalModule {
        @Provides
        @Singleton
        RolloutAdapter providesRolloutAdapter() {
            return rolloutAdapter;
        }

        @Provides @Singleton
        RolloutClient providesRolloutClient(RolloutAdapter adapter) {
            return new RolloutClient(adapter);
        }

    }


    public TimelineProcessorWrapper( NeuralNetEndpoint neuralNetEndpoint) {
        this.neuralNetEndpoint = neuralNetEndpoint;

        ObjectGraphRoot.getInstance().init(new RolloutLocalModule());
        features.clear();

        final PairingDAO pairingDAO = new HistoricalPairingDAO(deviceReadDAO, deviceDataReadAllSensorsDAO);

        this.timelineProcessor =  InstrumentedTimelineProcessor.createTimelineProcessor(
                pillDataReadDAO,deviceReadDAO,deviceDataReadAllSensorsDAO,
                ringTimeHistoryDAODynamoDB,feedbackDAO, sleepHmmDAO,accountDAO,sleepStatsDAO,
                new SenseDataDAODynamoDB(pairingDAO, deviceDataReadAllSensorsDAO, senseColorDAO, calibrationDAO),timeZoneHistoryDAO, priorsDAO,featureExtractionModelsDAO,
                defaultModelEnsembleDAO,userTimelineTestGroupDAO,
                sleepScoreParametersDAO,
                neuralNetEndpoint,algorithmConfiguration, metric);
    }


    private static List<Sample> samplesToSamples(final List<TimelineSensorDataProtos.Sample> samples,final double calibrationValue) {
        final List<Sample> samplesOutputList = Lists.newArrayList();
        for (final TimelineSensorDataProtos.Sample sample : samples) {
            samplesOutputList.add(new Sample(sample.getTimestamp(),(float)(calibrationValue * sample.getValue()),sample.getTzOffset()));
        }
        return samplesOutputList;
    }

    private static List<TrackerMotion> motionToMotions(final List<TimelineSensorDataProtos.TrackerMotion> motions) {
        final List<TrackerMotion> trackerMotions = Lists.newArrayList();

        for (final TimelineSensorDataProtos.TrackerMotion m : motions) {
            Long bitmask = null;

            //if (m.hasBitmask()) {
            //    bitmask = m.getBitmask();
            //}

            trackerMotions.add(
                        new TrackerMotion(0L,0L,Long.valueOf(0L),m.getTimestamp(),(int)m.getSvmMag(),(int)m.getTzOffset(),Long.valueOf(0),Long.valueOf(0),Long.valueOf(m.getOnDuration())));
        }

        return trackerMotions;
    }

    private void updateDAOs(TimelineSensorDataProtos.OneDaysSensorData data) {

        currentAccountId = data.getAccountId();
        currentTargetDate = DateTimeUtil.ymdStringToDateTime(data.getDateOfNight());

        allSensorSampleList = new AllSensorSampleList();

        //TODO calibrated based off of color and hardware version
        final double calibrationAudioCountsToDb = 1.0 / 1024.0;
        final double calibrationLightCountsToLux = 256.0 / (double)(1<<16);

        allSensorSampleList.add(Sensor.SOUND_NUM_DISTURBANCES,samplesToSamples(data.getAudioNumDisturbancesDbList(),1.0));
        allSensorSampleList.add(Sensor.SOUND_PEAK_DISTURBANCE,samplesToSamples(data.getAudioPeakDisturbanceDbList(),calibrationAudioCountsToDb));
        allSensorSampleList.add(Sensor.LIGHT,samplesToSamples(data.getAudioPeakDisturbanceDbList(),calibrationLightCountsToLux));
        allSensorSampleList.add(Sensor.WAVE_COUNT,samplesToSamples(data.getWavesList(),1.0));

        myMotions = motionToMotions(data.getMyMotionList());
        partnerMotions = motionToMotions(data.getPartnerMotionList());


        feedbackEvents = Lists.newArrayList();
        for (final TimelineSensorDataProtos.Event event : data.getTimelineFeedbackList()) {
            Event.Type type = null;
            switch (event.getEventType()) {

                case IN_BED:
                    type = Event.Type.IN_BED;
                    break;
                case SLEEP:
                    type = Event.Type.SLEEP;
                    break;
                case WAKE_UP:
                    type = Event.Type.WAKE_UP;
                    break;
                case OUT_OF_BED:
                    type = Event.Type.OUT_OF_BED;
                    break;

                default:
                    continue;
            }

            feedbackEvents.add(Event.createFromType(type,event.getTimestamp(),event.getTimestamp() + DateTimeConstants.MILLIS_PER_MINUTE,event.getTzOffset(),"",null,null));

        }


        if (!myMotions.isEmpty()) {
            tzOffset = myMotions.get(0).offsetMillis;
        }


        //TODO clear results storage


    }

    private TimelineProcessorOutput getOutput(final TimelineResult timelineResult) {
        //get events I want
        final List<Event> events = Lists.newArrayList();
        for (final Iterator<SleepSegment> it = timelineResult.timelines.get(0).events.iterator(); it.hasNext();) {
            final SleepSegment segment = it.next();

            if (SLEEP_EVENT_TYPES.contains(segment.getEvent().getType())) {
                //save event
                events.add(segment.getEvent());
            }
        }

        //get feedback

        return new TimelineProcessorOutput(events,feedbackEvents,sleepStatsResult,sleepScoreResult);

    }

    public Optional<TimelineProcessorOutput> setDataAndRun(final String base64) {
        try {

            setFeature("neural_net_algorithm",true);
            setFeature("pill_pair_motion_filter",true);
            setFeature("outlier_filter",false);
            setFeature("feedback_in_timeline",false);
            setFeature("sleep_score_no_motion_enforcement",false);
            setFeature("off_bed_hmm_motion_filter",false);
            setFeature("in_bed_search",false);
            setFeature("sound_events_use_higher_threshold",false);
            setFeature("sleep_stats_medium_sleep",false);
            setFeature("environment_in_timeline_score",false);
            setFeature("sleep_score_v4",false);
            setFeature("sleep_score_v5",true);
            setFeature("sleep_score_no_motion_enforcement",false);
            setFeature("timeline_in_sleep_insights",false);

            updateDAOs(TimelineSensorDataProtos.OneDaysSensorData.parseFrom(Base64.decodeBase64(base64)));

            final TimelineResult timelineResult = timelineProcessor.retrieveTimelinesFast(currentAccountId,currentTargetDate,Optional.<TimelineFeedback>absent());

            //TODO get results of timeline evaluation, pull sleep stats from DAO, form results and return as csv line
            if (timelineResult.timelines.isEmpty()) {
                return Optional.absent();
            }


            return Optional.of(getOutput(timelineResult));

        } catch (InvalidProtocolBufferException e) {
            e.printStackTrace();
        }


        return Optional.absent();
    }

}
